import pdfplumber
p = r'C:\Users\26112\Desktop\关于做好卫生健康系统软件正版化工作的通知.pdf'
with pdfplumber.open(p) as pdf:
    print('pages:', len(pdf.pages))
    for i, page in enumerate(pdf.pages):
        t = page.extract_text()
        print(f'page {i+1}: {len(t or "")} chars')
        print(repr((t or '')[:100]))