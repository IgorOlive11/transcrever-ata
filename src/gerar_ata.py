import os
from dotenv import load_dotenv
from openai import OpenAI
import docx
import tiktoken

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def dividir_texto_em_blocos(texto, max_tokens=3000):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(texto)
    blocos = []
    for i in range(0, len(tokens), max_tokens):
        bloco_tokens = tokens[i:i+max_tokens]
        bloco_texto = tokenizer.decode(bloco_tokens)
        blocos.append(bloco_texto)
    return blocos

def gerar_texto_formal(bloco_texto):
    prompt = f"""
Você é um redator profissional de atas de assembleia de condomínio.

Transforme o seguinte trecho da transcrição de uma assembleia em texto formal, claro, detalhado e narrativo, em norma culta, mantendo todas as informações e decisões.

IMPORTANTE:
- Não coloque cabeçalhos, títulos, datas, nomes de presidente ou secretário.
- Apenas transforme o conteúdo do trecho em texto formal, narrativo e coeso que futuramente integrará uma ATA final.
- Mantenha a sequência lógica dos fatos.

Trecho da transcrição:
{bloco_texto}

Produza o texto correspondente a esse trecho.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você reescreve transcrições em texto formal para atas de assembleia."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=3500,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Erro ao gerar texto formal: {e}")

def salvar_texto_docx(texto, caminho_arquivo, status_callback=None):
    doc = docx.Document()
    for linha in texto.split("\n"):
        if linha.strip():
            doc.add_paragraph(linha.strip())
        else:
            doc.add_paragraph("")
    doc.save(caminho_arquivo)
    if status_callback:
        status_callback(f"Arquivo salvo em {caminho_arquivo}")
    else:
        print(f"Arquivo salvo em {caminho_arquivo}")

def gerar_ata_formal(transcricao, caminho_saida="ata_gerada_parcial.docx", status_callback=None):
    blocos = dividir_texto_em_blocos(transcricao, max_tokens=3000)
    if status_callback:
        status_callback(f"Transcrição dividida em {len(blocos)} blocos.")
    else:
        print(f"Transcrição dividida em {len(blocos)} blocos.")

    textos_gerados = []
    for i, bloco in enumerate(blocos):
        if status_callback:
            status_callback(f"Gerando texto formal para bloco {i+1}/{len(blocos)}...")
        else:
            print(f"Gerando texto formal para bloco {i+1}/{len(blocos)}...")
        texto_formal = gerar_texto_formal(bloco)
        textos_gerados.append(texto_formal)

    texto_final = "\n\n".join(textos_gerados)
    salvar_texto_docx(texto_final, caminho_saida, status_callback=status_callback)
