
print("Pypdf")
import pypdf
reader = pypdf.PdfReader("relatorio.pdf")
texto = "\n".join([page.extract_text() for page in reader.pages])
print(texto)

print("_"*80)
print("CAMELOT")

import camelot

# Tente com flavor="stream" se lattice falhar
tabelas = camelot.read_pdf("relatorio.pdf", pages="1", flavor="stream")
print(f"Quantidade de tabelas: {len(tabelas)}")

# Iterar sobre as tabelas e exibir os dados
for i, tabela in enumerate(tabelas):
    print(f"\nTabela {i + 1}:")
    print(tabela.df) 