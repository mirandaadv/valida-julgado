# Valida Julgado

Plugin para advogados que precisam conferir citações de julgados brasileiros antes de
usá-las. Ele confere o dígito verificador do número CNJ, orienta a leitura da íntegra,
compara a decisão com o que a citação afirma e registra o resultado em uma ficha.

## Uso jurídico: revisão obrigatória

O plugin não dá orientação jurídica nem decide o que citar. Trabalho jurídico é caso de
alto risco na [Política de Uso da Anthropic](https://www.anthropic.com/legal/aup): um
profissional qualificado precisa revisar o resultado e poder alterá-lo, e quem receber a
orientação precisa ser informado claramente de que houve uso de IA.

## O que o plugin executa, envia ou busca

- **Executa** apenas `skills/valida-julgado/scripts/valida_cnj.py`, na máquina do
  usuário, só com a biblioteca padrão do Python. O script não acessa a rede e não grava
  arquivos.
- **Grava** a ficha `verificacao-julgados.md` na pasta de trabalho, por meio do Claude.
- **Envia ou busca:** nada por conta própria. O plugin não tem conector, hook nem endereço
  remoto, e não coleta dados. Se a sessão já tiver pesquisa de jurisprudência ou acesso à
  web, a skill pergunta antes de usar.

Os documentos que o usuário fornece são lidos pelo Claude, conforme a conta e as
configurações de dados do próprio usuário.

## Requisito

Python 3 (testado no 3.11), para conferir o dígito verificador. Sem ele, a ficha registra
"DV não conferido".

## Exemplos de uso

Os números abaixo são fictícios.

1. **Conferir números**

   > Confira estes números: 0000001-93.1900.8.26.0000 e 0000001-00.1900.8.26.0000.

   O primeiro tem DV correto, o que não prova que o processo exista. O segundo recebe
   `NÚMERO INVÁLIDO`, com DV esperado 93.

2. **Conferir uma citação com a íntegra**

   > Anexei o acórdão em PDF, baixado do portal do tribunal. Confira se ele decide a tese
   > que transcrevi nesta minuta.

   O Claude lê a íntegra, compara tese, transcrição e dados, e grava a ficha com o status.

3. **Triar lista recebida de terceiro ou de IA**

   > Recebi esta lista de julgados de uma ferramenta de IA. Valide cada um antes de eu
   > usar.

   O Claude confere os números, aponta sinais de citação gerada por IA e pede as íntegras
   que faltam.

## Status da ficha

| Status | Significado |
|---|---|
| `CONFIRMADO NA ÍNTEGRA` | Íntegra lida, de origem oficial identificada, e a citação confere |
| `ÍNTEGRA SEM ORIGEM CONFERIDA` | Íntegra lida e citação confere, mas sem origem oficial identificada |
| `DIVERGENTE` | Íntegra lida, mas tese, transcrição ou dados não conferem |
| `SÓ EMENTA` | Só a ementa foi lida |
| `NÃO LOCALIZADO` | Decisão não encontrada; conferência manual pendente |
| `NÚMERO INVÁLIDO` | DV ou formato não obedece ao padrão CNJ |

## Limites

- DV correto não prova que o processo exista. A regra está na
  [Resolução CNJ nº 65/2008](https://atos.cnj.jus.br/atos/detalhar/119), art. 1º, § 2º, e
  Anexo VIII.
- O plugin não verifica reforma posterior, trânsito em julgado nem vigência do
  entendimento.
- O plugin não atesta a autenticidade de arquivo sem origem oficial.
- O plugin não faz triagem de malware nem de texto oculto nos arquivos.
- A varredura por `--arquivo` lê só arquivo de texto. PDF e Word exigem extrair o texto
  antes; o script avisa e sai com código 2.

## Autoria

Marcos Eduardo Miranda e Eduardo Miranda Sociedade de Advogados.

## Suporte

contato@mirandaadv.com.br

## Licença

MIT. Veja o arquivo `LICENSE`.

## English summary

Valida Julgado helps lawyers check citations of Brazilian court decisions. It validates
the check digit of CNJ case numbers with a local script, guides a full reading of the
decision, compares it with the citation and records a status sheet. It has no connector,
hook or remote endpoint. A qualified professional must review the output.
