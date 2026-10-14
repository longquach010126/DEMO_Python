import codecs

with codecs.open('gui.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace any newlines inside string literals that cause unterminated errors
text = text.replace('v2.0\nPhát', 'v2.0\\nPhát')
text = text.replace('v2.0\r\nPhát', 'v2.0\\nPhát')
text = text.replace('Long\nỨng', 'Long\\nỨng')
text = text.replace('Long\r\nỨng', 'Long\\nỨng')

with codecs.open('gui.py', 'w', 'utf-8') as f:
    f.write(text)
