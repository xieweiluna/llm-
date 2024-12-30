import matplotlib.pyplot as plt
import pandas as pd

# 新的数据
data = {
    'Prompt Mode': ['COT-101', 'PS-201', 'PS+-302', 'POT-401'],
    'Total Questions': [20, 20, 20, 20],
    'Correct Answers': [11, 13, 16, 16],
    'Accuracy': [0.5500, 0.6500, 0.8000, 0.8000]
}

# 将数据转换为 Pandas DataFrame，方便处理和绘图
df = pd.DataFrame(data)

# 1. 比较不同 Prompt Mode 的准确率 (柱状图)
plt.figure(figsize=(10, 6))
plt.bar(df['Prompt Mode'], df['Accuracy'], color=['skyblue', 'lightcoral', 'lightgreen', 'lightsalmon'])
plt.xlabel('Prompt Mode')
plt.ylabel('Accuracy')
plt.title('Accuracy Comparison of Different Prompt Modes')
plt.ylim(0, 1)  # 设置 y 轴范围为 0 到 1
plt.grid(axis='y', linestyle='--')
plt.tight_layout()
plt.show()

# 2. 比较不同 Prompt Mode 的正确答案数量 (柱状图)
plt.figure(figsize=(10, 6))
plt.bar(df['Prompt Mode'], df['Correct Answers'], color=['skyblue', 'lightcoral', 'lightgreen', 'lightsalmon'])
plt.xlabel('Prompt Mode')
plt.ylabel('Correct Answers')
plt.title('Correct Answers Comparison of Different Prompt Modes')
plt.grid(axis='y', linestyle='--')
plt.tight_layout()
plt.show()

# 3. 绘制准确率的水平条形图，并标记准确率数值
plt.figure(figsize=(10, 6))
plt.barh(df['Prompt Mode'], df['Accuracy'], color=['skyblue', 'lightcoral', 'lightgreen', 'lightsalmon'])
plt.xlabel('Accuracy')
plt.ylabel('Prompt Mode')
plt.title('Accuracy of Different Prompt Modes')
plt.xlim(0, 1)  # 设置 x 轴范围为 0 到 1
for i, v in enumerate(df['Accuracy']):
    plt.text(v + 0.01, i, str(round(v, 4)), color='black', va='center') # 在条形图上添加数值
plt.grid(axis='x', linestyle='--')
plt.tight_layout()
plt.show()

# 4. 绘制饼图显示不同 Prompt Mode 的准确率占比 (需要注意饼图的适用性，这里只是作为示例)
plt.figure(figsize=(8, 8))
plt.pie(df['Accuracy'], labels=df['Prompt Mode'], autopct='%1.1f%%', startangle=90, colors=['skyblue', 'lightcoral', 'lightgreen', 'lightsalmon'])
plt.title('Accuracy Distribution Across Prompt Modes')
plt.tight_layout()
plt.show()

# 5. (可选) 绘制散点图，用总问题数作为 x 轴，正确答案数作为 y 轴，点的大小或颜色表示准确率
plt.figure(figsize=(10, 6))
plt.scatter(df['Total Questions'], df['Correct Answers'], s=df['Accuracy'] * 500, c=df['Accuracy'], cmap='viridis', alpha=0.7)
plt.xlabel('Total Questions')
plt.ylabel('Correct Answers')
plt.title('Relationship between Total Questions, Correct Answers and Accuracy')
plt.colorbar(label='Accuracy')
for i, txt in enumerate(df['Prompt Mode']):
    plt.annotate(txt, (df['Total Questions'][i], df['Correct Answers'][i]), textcoords="offset points", xytext=(5,5), ha='left')
plt.grid(True)
plt.tight_layout()
plt.show()