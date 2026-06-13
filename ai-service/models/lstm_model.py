import csv
import json
import os

import torch
import torch.nn as nn


AI_SERVICE_DIR = os.path.dirname(os.path.dirname(__file__))
DEFAULT_WEIGHTS_PATH = os.path.join(AI_SERVICE_DIR, "weights", "lstm_best.pth")
DEFAULT_MAPPING_PATH = os.path.join(AI_SERVICE_DIR, "data", "product_mapping.json")
DEFAULT_INTERACTIONS_CSV = os.path.join(AI_SERVICE_DIR, "user_interactions.csv")


class LSTMModel(nn.Module):
    def __init__(self, num_products, embedding_dim=32, hidden_dim=64):
        super().__init__()
        # Product indices are shifted by 1 at input time so 0 is reserved for padding.
        self.embedding = nn.Embedding(num_products + 1, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_products)

    def forward(self, x):
        emb = self.embedding(x)
        out, _ = self.lstm(emb)
        out = out[:, -1, :]
        return self.fc(out)


class LSTMRecommendationEngine:
    def __init__(self, weights_path=None, mapping_path=None):
        self.model = None
        self.id_to_idx = {}
        self.idx_to_id = {}
        self.num_products = 0

        self.weights_path = weights_path or DEFAULT_WEIGHTS_PATH
        self.mapping_path = mapping_path or DEFAULT_MAPPING_PATH

        self.load_mapping(self.mapping_path)
        if self.num_products > 0:
            self.model = LSTMModel(self.num_products)
            self.load_weights(self.weights_path)
            self.model.eval()

    def load_mapping(self, mapping_path):
        if not os.path.exists(mapping_path):
            print(f"Mapping file not found at {mapping_path}. LSTM will remain uninitialized.")
            return

        with open(mapping_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.id_to_idx = data.get("id_to_idx", {})
            self.idx_to_id = data.get("idx_to_id", {})
            self.num_products = len(self.id_to_idx)
            print(f"Loaded mapping for {self.num_products} products.")

    def load_weights(self, weights_path):
        if not self.model or not os.path.exists(weights_path):
            print("LSTM weights file not found. Using random weights.")
            return

        try:
            self.model.load_state_dict(torch.load(weights_path, map_location=torch.device("cpu")))
            print(f"LSTM weights loaded from {weights_path}.")
        except Exception as e:
            print(f"Failed to load LSTM weights: {e}")

    def extract_user_sequence_from_csv(self, user_id, filepath=None, max_seq_len=10):
        """
        Read the latest product-id sequence for a user from user_interactions.csv.
        The result is intentionally a list of product IDs, matching predict_next_products().
        """
        filepath = filepath or DEFAULT_INTERACTIONS_CSV
        if not os.path.exists(filepath):
            return []

        interactions = []
        try:
            with open(filepath, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if str(row.get("user_id")) != str(user_id):
                        continue

                    product_id = str(row.get("product_id", "")).strip()
                    if product_id not in self.id_to_idx:
                        continue

                    interactions.append(
                        {
                            "product_id": product_id,
                            "timestamp": row.get("timestamp", ""),
                        }
                    )
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []

        interactions = sorted(interactions, key=lambda item: item["timestamp"])
        return [int(item["product_id"]) for item in interactions[-max_seq_len:]]

    def predict_next_products(self, user_sequence, top_k=5):
        """
        user_sequence: list of product dicts or product IDs representing the sequence.
        Returns a list of top_k product IDs.
        """
        if not self.model or not user_sequence:
            return []

        idx_sequence = []
        for item in user_sequence:
            product_id = None
            if isinstance(item, dict):
                product_id = item.get("id") or item.get("product_id")
            elif isinstance(item, (int, str)):
                product_id = item

            product_id = str(product_id)
            if product_id in self.id_to_idx:
                idx_sequence.append(self.id_to_idx[product_id] + 1)

        if not idx_sequence:
            return []

        try:
            x = torch.tensor([idx_sequence], dtype=torch.long)
            with torch.no_grad():
                output = self.model(x)

            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            top_k_actual = min(top_k, self.num_products)
            top_indices = torch.topk(probabilities, k=top_k_actual).indices.tolist()

            return [
                int(self.idx_to_id[str(idx)])
                for idx in top_indices
                if str(idx) in self.idx_to_id
            ]
        except Exception as e:
            print(f"Error in LSTM prediction: {e}")
            return []
