# Tài liệu Kiến trúc AI: Gợi ý Sản phẩm & Chatbot

Hệ thống **AI Service** của ShopVN được thiết kế dựa trên một kiến trúc Microservice độc lập (viết bằng FastAPI), tích hợp các kỹ thuật Machine Learning tiên tiến nhất hiện nay để mang lại trải nghiệm cá nhân hóa cho người dùng.

Dưới đây là giải thích chi tiết về luồng hoạt động của 2 tính năng cốt lõi: Gợi ý sản phẩm (Recommendations) và Chatbot AI.

---

## 1. Khởi tạo & Nạp dữ liệu (Data Ingestion)

Mô hình AI chỉ hoạt động tốt khi có dữ liệu. Do đó, ngay khi `ai-service` khởi động (trong `main.py`), hệ thống sẽ thực hiện quá trình sau:
1. **Gọi API nội bộ:** AI Service tự động kết nối đến `product-service` (qua mạng Docker nội bộ) để fetch toàn bộ danh sách sản phẩm đang "Active".
2. **Nạp vào Graph DB (Neo4j):** Tạo các node `Product` và xây dựng các mối quan hệ `[:SIMILAR]` (tương tự) giữa các sản phẩm dựa trên thuộc tính và danh mục.
3. **Nạp vào Vector DB (FAISS):** Kết hợp Tên, Mô tả, và Danh mục của sản phẩm thành một câu hoàn chỉnh, sau đó dùng mô hình **Sentence-Transformers** (`all-MiniLM-L6-v2`) để mã hóa đoạn text đó thành một vector không gian (embeddings) và lưu vào bộ nhớ FAISS.

> [!TIP]
> Nhờ cơ chế này, AI Service không bao giờ bị "cũ" dữ liệu. Nếu có sản phẩm mới, bạn có thể gọi API `POST /api/ai/reload/` để AI tự động học lại kho hàng mới nhất.

---

## 2. Tính năng Gợi ý Sản phẩm (Hybrid Recommendation)

Khi người dùng vào xem chi tiết một sản phẩm (ví dụ `products/1`), giao diện sẽ gọi API `/api/recommendations/1/`. Thay vì chỉ query database thông thường, hệ thống sử dụng một **Hybrid Recommendation Engine** (mô hình lai) kết hợp 3 thuật toán:

### A. LSTM (Deep Learning - Sequence Modeling)
- **Cơ chế:** LSTM là mạng nơ-ron hồi quy chuyên xử lý chuỗi. Nó nhìn vào lịch sử (sequence) click/xem/mua của người dùng.
- **Tác dụng:** Hiểu được "hành trình" của khách hàng. Ví dụ: Khách vừa xem *Mainboard* -> xem *CPU* -> LSTM sẽ dự đoán sản phẩm tiếp theo họ muốn xem là *RAM* hoặc *VGA*.

### B. Knowledge Graph (Neo4j - Graph Database)
- **Cơ chế:** Khai phá dữ liệu dạng đồ thị (nodes và edges). Query Cypher sẽ tìm kiếm theo mẫu: `User -> [:BUY] -> Product A -> [:SIMILAR] -> Product B`.
- **Tác dụng:** Tìm ra các mối quan hệ phức tạp mà SQL thông thường rất khó làm (Ví dụ: Những người giống bạn đã mua gì? Các sản phẩm mua kèm thường xuyên là gì?).

### C. RAG Semantic (Tìm kiếm ngữ nghĩa)
- Tìm các sản phẩm có ý nghĩa văn bản tương đồng với sản phẩm đang xem.

### D. Tổng hợp (Hybrid Aggregation)
Mô hình `HybridRecommendationEngine` sẽ thu thập kết quả từ cả 3 thuật toán trên, sau đó **nhân với các trọng số** (ví dụ: LSTM 40%, Graph 40%, Semantic 20%) để tính ra điểm số tổng (Score) cao nhất và trả về Top 4 - Top 8 sản phẩm cho giao diện.

---

## 3. Tính năng AI Chatbot (RAG Pipeline)

Chatbot của hệ thống (nút nổi ở góc phải màn hình) được xây dựng dựa trên kỹ thuật **RAG (Retrieval-Augmented Generation)**. Khác với các chatbot dùng rule-based (if/else) truyền thống, chatbot này có khả năng "hiểu" ngôn ngữ tự nhiên.

Luồng hoạt động khi bạn chat "tìm cho mình laptop chơi game giá rẻ":

1. **User Query Vectorization:** 
   Câu chat của bạn được đưa qua `Sentence-Transformer` để biến thành một vector số thực (embedding).
   
2. **Similarity Search (FAISS):** 
   Vector câu chat của bạn được mang đi so sánh với hàng ngàn vector sản phẩm đã lưu sẵn trong FAISS (bằng thuật toán tính khoảng cách Cosine hoặc L2). FAISS sẽ ngay lập tức trích xuất (Retrieve) ra Top 4 sản phẩm có khoảng cách gần nhất (nghĩa là có ngữ nghĩa phù hợp nhất với câu chat).
   
3. **Generation (Tạo câu trả lời):** 
   Thay vì chỉ trả về một mảng JSON nhàm chán, AI sẽ lắp ghép kết quả vào một ngôn ngữ giao tiếp tự nhiên (Mocked LLM) và cấu trúc lại dữ liệu để gửi về cho Frontend.
   
4. **Hiển thị trên UI:** 
   Component `ChatBot.jsx` nhận dữ liệu, hiển thị bong bóng chat với hiệu ứng đánh chữ (typing indicator), và render các Card Sản phẩm ngay bên trong khung chat. Người dùng có thể click thẳng vào Card để chuyển đến trang mua hàng.

> [!NOTE]
> Trong môi trường Production thực tế, bước Generation thường được đẩy prompt sang các LLM lớn như OpenAI GPT-4 hay Gemini để câu trả lời có tính "người" hơn. Hiện tại hệ thống đang dùng hàm tạo text nội bộ để tiết kiệm chi phí API và tăng tốc độ phản hồi.

---

## 4. Ưu điểm của Kiến trúc

- **Tách biệt hoàn toàn (Decoupled):** AI Service chạy riêng biệt trên cổng `8006`, dùng thư viện Python riêng. Việc AI xử lý nặng không làm ảnh hưởng đến tốc độ của Product Service hay Cart Service.
- **Dễ dàng nâng cấp:** Có thể thay thế mô hình Sentence-Transformers bằng các mô hình nhúng mạnh hơn (như text-embedding-3-small) chỉ bằng cách đổi tên string config.
- **Trải nghiệm người dùng cao (UX):** Chatbot UI được thiết kế theo phong cách Glassmorphism, có hiệu ứng chuyển cảnh mượt mà và gợi ý sản phẩm trực quan, mang lại cảm giác của một nền tảng thương mại điện tử cao cấp.
