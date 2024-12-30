import json
import random

def load_data(lines_file, labels_file):
    """Loads news articles and their corresponding labels."""
    with open(lines_file, 'r', encoding='utf-8') as f:
        content = f.read()
        news_articles = [article.strip() for article in content.split('\n') if article.strip()]

    with open(labels_file, 'r', encoding='utf-8') as f:
        labels = [int(line.strip()) for line in f]

    return news_articles, labels

def prepare_json_data(news_articles, labels, num_samples=10):
    """Prepares JSON data by randomly selecting true and false news."""
    true_news = []
    false_news = []

    for i in range(len(news_articles)):
        if i < len(labels): # 确保索引不超过 labels 的范围
            if labels[i] == 0:  # 0 代表假新闻
                false_news.append(news_articles[i])
            elif labels[i] == 1: # 1 代表真新闻
                true_news.append(news_articles[i])

    sampled_data = []
    if len(true_news) >= num_samples:
        sampled_true = random.sample(true_news, num_samples)
        for news in sampled_true:
            sampled_data.append({"question": news+'Please tell me if this news is true or false. Only answer with "true" or "false".', "answer": True})
    else:
        print(f"Warning: Only {len(true_news)} true news available, cannot sample {num_samples}.")
        for news in true_news:
            sampled_data.append({"question": news+'Please tell me if this news is true or false. Only answer with "true" or "false".', "answer": True})

    if len(false_news) >= num_samples:
        sampled_false = random.sample(false_news, num_samples)
        for news in sampled_false:
            sampled_data.append({"question": news+'Please tell me if this news is true or false. Only answer with "true" or "false".', "answer": False})
    else:
        print(f"Warning: Only {len(false_news)} false news available, cannot sample {num_samples}.")
        for news in false_news:
            sampled_data.append({"question": news+'Please tell me if this news is true or false. Only answer with "true" or "false".', "answer": False})

    random.shuffle(sampled_data)  # Shuffle the combined data
    return sampled_data

# Load the data
news_articles, labels = load_data('gossipcop_lines.txt', 'gossipcop_label.txt')

# Prepare the JSON data
json_data = prepare_json_data(news_articles, labels)

# Write to a JSON file
with open('sampled_news.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=2, ensure_ascii=False)

print("Sampled news data saved to sampled_news.json")