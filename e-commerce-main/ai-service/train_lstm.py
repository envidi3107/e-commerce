import argparse
import csv
import json
import os
from collections import Counter, defaultdict

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split

from models.lstm_model import LSTMModel


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")

CSV_FILE = os.path.join(BASE_DIR, "user_interactions.csv")
INTERACTIONS_FILE = os.path.join(DATA_DIR, "user_interactions.json")
MAPPING_FILE = os.path.join(DATA_DIR, "product_mapping.json")
WEIGHTS_FILE = os.path.join(WEIGHTS_DIR, "lstm_best.pth")

VALID_EVENTS = {"view", "add_to_cart", "buy"}


class InteractionDataset(Dataset):
    def __init__(self, sequences, max_len=15):
        self.samples = []
        self.max_len = max_len

        for seq in sequences:
            for i in range(1, len(seq)):
                input_seq = seq[:i][-self.max_len :]
                target = seq[i]
                self.samples.append((input_seq, target))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        input_seq, target = self.samples[idx]

        # Product indices are shifted by 1 in the embedding input so 0 can be padding.
        shifted_seq = [product_idx + 1 for product_idx in input_seq]
        pad_len = self.max_len - len(shifted_seq)
        padded_seq = [0] * pad_len + shifted_seq

        return torch.tensor(padded_seq, dtype=torch.long), torch.tensor(target, dtype=torch.long)


def parse_args():
    parser = argparse.ArgumentParser(description="Prepare CSV interactions and train the LSTM recommender.")
    parser.add_argument("--csv", default=CSV_FILE, help="Path to user_interactions.csv")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--max-len", type=int, default=15)
    parser.add_argument("--lr", type=float, default=0.005)
    parser.add_argument("--min-product-events", type=int, default=5)
    parser.add_argument("--no-prepare", action="store_true", help="Skip CSV -> JSON/mapping preparation.")
    return parser.parse_args()


def prepare_data_from_csv(csv_path, min_product_events=5):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rows_by_user = defaultdict(list)
    product_counts = Counter()

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                user_id = int(row["user_id"])
                product_id = int(row["product_id"])
            except (KeyError, TypeError, ValueError):
                continue

            event_type = row.get("event_type", "").strip().lower()
            timestamp = row.get("timestamp", "").strip()
            if event_type not in VALID_EVENTS or not timestamp:
                continue

            rows_by_user[user_id].append(
                {
                    "product_id": product_id,
                    "action": event_type.upper(),
                    "timestamp": timestamp,
                }
            )
            product_counts[product_id] += 1

    frequent_products = {
        product_id for product_id, count in product_counts.items() if count >= min_product_events
    }
    if len(frequent_products) < 2:
        frequent_products = set(product_counts)

    interactions = []
    filtered_product_ids = set()

    for user_id, rows in sorted(rows_by_user.items()):
        sorted_rows = sorted(rows, key=lambda item: item["timestamp"])
        user_events = [
            row for row in sorted_rows if row["product_id"] in frequent_products
        ]
        if len(user_events) < 2:
            continue

        for event in user_events:
            filtered_product_ids.add(event["product_id"])

        interactions.append(
            {
                "user_id": user_id,
                "interactions": user_events,
            }
        )

    product_ids = sorted(filtered_product_ids)
    id_to_idx = {str(product_id): idx for idx, product_id in enumerate(product_ids)}
    idx_to_id = {str(idx): product_id for product_id, idx in id_to_idx.items()}

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(INTERACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(interactions, f, ensure_ascii=False, indent=2)
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "id_to_idx": id_to_idx,
                "idx_to_id": idx_to_id,
                "source_csv": os.path.abspath(csv_path),
                "min_product_events": min_product_events,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    total_events = sum(len(user["interactions"]) for user in interactions)
    print(
        f"Prepared {total_events} events from {len(interactions)} users "
        f"and {len(product_ids)} products."
    )


def load_sequences():
    if not os.path.exists(MAPPING_FILE) or not os.path.exists(INTERACTIONS_FILE):
        raise FileNotFoundError("Data files not found. Run train_lstm.py without --no-prepare first.")

    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)
        id_to_idx = mapping.get("id_to_idx", {})

    with open(INTERACTIONS_FILE, "r", encoding="utf-8") as f:
        interactions = json.load(f)

    sequences = []
    for user in interactions:
        seq = []
        for interaction in user.get("interactions", []):
            product_id = str(interaction.get("product_id"))
            if product_id in id_to_idx:
                seq.append(id_to_idx[product_id])
        if len(seq) > 1:
            sequences.append(seq)

    return sequences, len(id_to_idx), len(interactions)


def main():
    args = parse_args()

    if not args.no_prepare:
        prepare_data_from_csv(args.csv, min_product_events=args.min_product_events)

    sequences, num_products, num_users = load_sequences()
    print(f"Loaded {num_products} products and {num_users} users.")
    print(f"Created {len(sequences)} valid user sequences.")

    dataset = InteractionDataset(sequences, max_len=args.max_len)
    if len(dataset) == 0:
        raise RuntimeError("No training samples were created. Check your CSV interactions.")

    val_size = max(1, int(len(dataset) * 0.1)) if len(dataset) > 10 else 0
    train_size = len(dataset) - val_size

    if val_size:
        train_dataset, val_dataset = random_split(
            dataset,
            [train_size, val_size],
            generator=torch.Generator().manual_seed(20260610),
        )
    else:
        train_dataset, val_dataset = dataset, None

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = (
        DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
        if val_dataset
        else None
    )
    print(f"Created dataset with {len(dataset)} samples ({train_size} train, {val_size} val).")

    model = LSTMModel(num_products)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    best_loss = float("inf")
    best_state = None

    print("Starting training...")
    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        avg_train_loss = train_loss / len(train_loader)

        if val_loader:
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for inputs, targets in val_loader:
                    outputs = model(inputs)
                    val_loss += criterion(outputs, targets).item()
            avg_val_loss = val_loss / len(val_loader)
        else:
            avg_val_loss = avg_train_loss

        if avg_val_loss < best_loss:
            best_loss = avg_val_loss
            best_state = model.state_dict()

        print(
            f"Epoch {epoch + 1}/{args.epochs} - "
            f"train_loss={avg_train_loss:.4f} val_loss={avg_val_loss:.4f}"
        )

    torch.save(best_state or model.state_dict(), WEIGHTS_FILE)
    print(f"Training completed. Best val loss: {best_loss:.4f}")
    print(f"Weights saved to {WEIGHTS_FILE}.")


if __name__ == "__main__":
    main()
