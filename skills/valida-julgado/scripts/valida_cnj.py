# -*- coding: utf-8 -*-
"""Confere o digito verificador (DV) de numeros de processo no padrao CNJ.

Norma: Resolucao CNJ n. 65/2008, art. 1, par. 2, e Anexo VIII (Modulo 97 Base 10,
ISO 7064:2003). DD = 98 - ((NNNNNNN AAAA J TR OOOO + "00") mod 97).

Uso (o numero do exemplo e ficticio):
  python valida_cnj.py 0000001-93.1900.8.26.0000 [outro ...]
  python valida_cnj.py --arquivo texto.md [outro.txt ...]
  python valida_cnj.py --json ...

Codigo de saida:
  0 = todos os numeros com DV correto
  1 = algum numero com DV errado ou formato invalido
  2 = conferencia incompleta: sem argumento, arquivo ilegivel ou nao textual,
      ou nenhum numero encontrado no texto

DV errado: o numero nao obedece a regra do CNJ.
DV certo: NAO prova que o processo existe nem que a citacao esta correta.

Usa so a biblioteca padrao. Nao acessa a rede e nao grava arquivos.
"""
import json
import re
import sys

CNJ = re.compile(r"(\d{7})-(\d{2})\.(\d{4})\.(\d)\.(\d{2})\.(\d{4})")

# Tudo o que parece numero CNJ, inclusive incompleto ou mal pontuado. Assim o numero
# malformado aparece no relatorio em vez de ser ignorado na varredura de texto.
CANDIDATO = re.compile(r"(?<!\d)\d{1,7}-\d{1,2}\.\d{4}\.\d{1,3}(?:\.\d{1,4}){0,2}(?!\d)")

ASSINATURAS_NAO_TEXTO = (b"%PDF", b"PK\x03\x04", b"{\\rtf")

# Anexos da Resolucao CNJ n. 65/2008: TR 01 a 27 na Justica dos Estados e do DF.
TJ_POR_TR = "AC AL AP AM BA CE DFT ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SE SP TO".split()


def dv_esperado(n, a, j, tr, o):
    return 98 - (int(f"{n}{a}{j}{tr}{o}00") % 97)


def tribunal(j, tr):
    t = int(tr)
    if t == 0 and j in ("1", "2", "3", "5"):
        return {"1": "STF", "2": "CNJ", "3": "STJ", "5": "TST"}[j]
    if j == "4" and 1 <= t <= 6:
        return f"TRF{t}"
    if j == "5" and 1 <= t <= 24:
        return f"TRT{t}"
    if j == "8" and 1 <= t <= 27:
        return "TJ" + TJ_POR_TR[t - 1]
    return f"J{j}/TR{tr}"


def validar(numero):
    texto = numero.strip()
    if re.fullmatch(r"\d{20}", texto):
        texto = f"{texto[:7]}-{texto[7:9]}.{texto[9:13]}.{texto[13]}.{texto[14:16]}.{texto[16:]}"
    m = CNJ.fullmatch(texto)
    if not m:
        return {"numero": texto, "formato": "invalido", "valido": False}
    n, d, a, j, tr, o = m.groups()
    esperado = dv_esperado(n, a, j, tr, o)
    return {
        "numero": texto,
        "formato": "ok",
        "dv_informado": int(d),
        "dv_esperado": esperado,
        "valido": int(d) == esperado,
        "tribunal": tribunal(j, tr),
        "ano": int(a),
        "origem": o,
    }


def varrer_texto(texto):
    vistos, saida = set(), []
    for m in CANDIDATO.finditer(texto):
        numero = m.group(0)
        if numero not in vistos:
            vistos.add(numero)
            saida.append(validar(numero))
    return saida


def ler_texto(caminho):
    with open(caminho, "rb") as f:
        dados = f.read()
    if dados.startswith(ASSINATURAS_NAO_TEXTO) or b"\0" in dados:
        raise ValueError("arquivo nao textual; extraia o texto e rode de novo")
    return dados.decode("utf-8", errors="replace")


def main(argv):
    for fluxo in (sys.stdout, sys.stderr):
        fluxo.reconfigure(errors="replace")
    como_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    if not args or args == ["--arquivo"]:
        print(__doc__, file=sys.stderr)
        return 2

    resultados, erros = [], []
    if args[0] == "--arquivo":
        for caminho in args[1:]:
            try:
                resultados.extend(varrer_texto(ler_texto(caminho)))
            except (OSError, ValueError) as e:
                erros.append(f"{caminho}: {e}")
        if not resultados and not erros:
            erros.append("nenhum numero no padrao CNJ encontrado no texto")
    else:
        resultados = [validar(a) for a in args]

    if como_json:
        print(json.dumps({"resultados": resultados, "erros": erros}, ensure_ascii=False, indent=2))
    else:
        for r in resultados:
            if r["formato"] != "ok":
                print(f"{r['numero']}: FORMATO INVALIDO")
            elif r["valido"]:
                print(f"{r['numero']}: DV OK | {r['tribunal']} | {r['ano']}")
            else:
                print(f"{r['numero']}: DV INVALIDO (esperado {r['dv_esperado']:02d}) | {r['tribunal']} | {r['ano']}")
        for erro in erros:
            print(f"NAO CONFERIDO: {erro}", file=sys.stderr)

    if erros:
        return 2
    return 0 if all(r["valido"] for r in resultados) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
