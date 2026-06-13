import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageCircle, X, Send, Bot, Sparkles } from 'lucide-react'
import { chatApi } from '../api'
import './ChatBot.css'

const WELCOME_MSG = {
  role: 'bot',
  text: 'Xin chào! 👋 Tôi là trợ lý mua sắm AI của ShopVN.\n\nBạn muốn tìm sản phẩm gì hôm nay?',
  products: [],
}

const QUICK_ACTIONS = [
  'Laptop gaming',
  'Điện thoại',
  'Sách hay',
  'Kem chống nắng',
  'Tai nghe',
  'Thời trang nam',
]

export default function ChatBot() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([WELCOME_MSG])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const navigate = useNavigate()

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Focus input when panel opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 350)
    }
  }, [open])

  const sendMessage = async (text) => {
    const query = (text || input).trim()
    if (!query || loading) return

    // Add user message
    const userMsg = { role: 'user', text: query, products: [] }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const { data } = await chatApi.send(query)
      const botMsg = {
        role: 'bot',
        text: data.text || 'Xin lỗi, tôi không hiểu câu hỏi của bạn.',
        products: data.products || [],
      }
      setMessages(prev => [...prev, botMsg])
    } catch {
      setMessages(prev => [
        ...prev,
        {
          role: 'bot',
          text: 'Xin lỗi, tôi đang gặp sự cố kết nối. Vui lòng thử lại sau! 😅',
          products: [],
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage()
  }

  const handleProductClick = (productId) => {
    navigate(`/products/${productId}`)
    setOpen(false)
  }

  const formatPrice = (price) => {
    return Number(price).toLocaleString('vi-VN') + '₫'
  }

  return (
    <>
      {/* Floating toggle button */}
      <button
        className={`chatbot-toggle ${open ? 'open' : ''}`}
        onClick={() => setOpen(!open)}
        title={open ? 'Đóng chat' : 'Chat với AI'}
        id="chatbot-toggle-btn"
      >
        {open ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="chatbot-panel" id="chatbot-panel">
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-avatar">
              <Sparkles size={20} />
            </div>
            <div className="chatbot-header-info">
              <h4>ShopVN AI Assistant</h4>
              <p>Trực tuyến — Sẵn sàng hỗ trợ</p>
            </div>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-msg ${msg.role}`}>
                <div className="chat-msg-bubble">
                  {/* Render text with line breaks */}
                  {msg.text.split('\n').map((line, j) => (
                    <span key={j}>
                      {line.startsWith('**') && line.endsWith('**')
                        ? <strong>{line.slice(2, -2)}</strong>
                        : line.startsWith('👉 **')
                          ? <>{line.split('**').map((part, k) =>
                              k % 2 === 1 ? <strong key={k}>{part}</strong> : part
                            )}</>
                          : line
                      }
                      {j < msg.text.split('\n').length - 1 && <br />}
                    </span>
                  ))}
                </div>

                {/* Product cards */}
                {msg.products?.length > 0 && (
                  <div className="chat-products">
                    {msg.products.map(p => (
                      <div
                        key={p.id}
                        className="chat-product-card"
                        onClick={() => handleProductClick(p.id)}
                      >
                        <div className="chat-product-img">
                          {p.thumbnail ? (
                            <img src={p.thumbnail} alt={p.name} />
                          ) : (
                            <Bot size={24} style={{ opacity: 0.3 }} />
                          )}
                        </div>
                        <div className="chat-product-name">{p.name}</div>
                        <div className="chat-product-price">
                          {formatPrice(p.price)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Quick actions after welcome message */}
                {i === 0 && msg.role === 'bot' && (
                  <div className="chat-quick-actions">
                    {QUICK_ACTIONS.map(q => (
                      <button
                        key={q}
                        className="chat-quick-btn"
                        onClick={() => sendMessage(q)}
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="chat-msg bot">
                <div className="chat-msg-bubble">
                  <div className="typing-indicator">
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <form className="chatbot-input" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              type="text"
              placeholder="Hỏi tôi về sản phẩm..."
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
              id="chatbot-input"
            />
            <button
              type="submit"
              className="chatbot-send-btn"
              disabled={!input.trim() || loading}
              title="Gửi"
              id="chatbot-send-btn"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      )}
    </>
  )
}
