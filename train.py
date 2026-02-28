from __future__ import annotations

from coolsense.optimizer.training import train_model


def main() -> None:
    artifact = train_model(model_path="coolsense_model.pt", n_scenarios=500, seed=42)
    print(f"Trained model with {artifact['sample_count']} samples")


if __name__ == "__main__":
    main()
