from datasets import Dataset, Image, DatasetDict
import json
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json_path",
        type=str,
        default="data/data.json",
    )
    parser.add_argument(
        "--repo_name",
        type=str,
    )

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    # JSON 불러오기
    with open(args.json_path, "r") as f:
        data = [json.loads(line) for line in f]
    print(len(data))

    # Dataset으로 변환
    dataset = DatasetDict()
    dataset["train"] = Dataset.from_list(data[:int(len(data) * 0.8)])
    dataset["valid"] = Dataset.from_list(data[int(len(data) * 0.8):int(len(data) * 0.9)])
    dataset["test"] = Dataset.from_list(data[int(len(data) * 0.9):])

    print(len(dataset["train"]))
    print(len(dataset["valid"]))
    print(len(dataset["test"]))

    # 이미지 경로 필드를 Image 타입으로 변환
    dataset["train"] = dataset["train"].cast_column("input_image", Image())
    dataset["train"] = dataset["train"].cast_column("output_image", Image())
    dataset["valid"] = dataset["valid"].cast_column("input_image", Image())
    dataset["valid"] = dataset["valid"].cast_column("output_image", Image())
    dataset["test"] = dataset["test"].cast_column("input_image", Image())
    dataset["test"] = dataset["test"].cast_column("output_image", Image())

    dataset.push_to_hub(args.hub_name)


if __name__ == "__main__":
    main()
