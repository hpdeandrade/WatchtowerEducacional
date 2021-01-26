# Watchtower Educacional
Watchtower Educacional é um projeto de compartilhamento de conteúdo educacional nos campos de trading, programação e finanças. A iniciativa é coordenada pelos desenvolvedores da Watchtower, um sistema de trading algorítmico escrito em Python com aplicações nos mercados de ações, cambial, juros e crypto.

# Disclaimer
Todo o material compartilhado possui fins educativos apenas. Não coloque em risco dinheiro que você não está disposto a perder. Use os softwares disponibilizados por sua conta e risco. Nenhum dos autores e afiliados assume quaisquer responsabilidades pelos seus resultados ao operar no mercado.

# 2 - Algo trading: implementando análises técnica e fundamentalista com Python
### Requerimentos
* [Python 3.8.6](https://www.python.org/downloads/release/python-386/)
* [MetaTrader5](https://www.metatrader5.com/en)
* [virtualenv](https://virtualenv.pypa.io/en/latest/) (recomendável)
* [TA-Lib](https://mrjbq7.github.io/ta-lib/) (instruções para instalação abaixo)

# Instalação
### Instalando o software do MetaTrader5
Após instalado, faça login com as credenciais de sua corretora de escolha (ex: Rico, Clear ou XP). Além disso, é necessário habilitar a função *Algo Trading* dentro do MetaTrader5.

### Instalando o Python e instanciando um ambiente virtual para o projeto
Após instalar o Python, certifique-se de adicioná-lo ao PATH ao final da instalação. Em seguida, através da biblioteca virtualenv, vamos configurar um ambiente virtual para o projeto. Essa etapa é opcional e permite que você trabalhe com uma versão mais *clean* do Python, inteiramente dedicada ao projeto. Isso significa que as bibliotecas instaladas não irão se misturar com as da instalação original do Python na sua máquina. Para instalar o virtualenv, execute o comando `pip install virtualenv` no terminal.

Para criar o ambiente virtual, `cd` para a pasta do projeto (preferivelmente) e então execute `virtualenv MYENV` no terminal. Substitua `MYENV` por algo de sua escolha. Uma nova instância do Python foi criada!

O último passo é ativar o ambiente virtual criado. Execute `MYENV/scripts/activate` e pronto! Agora você está pronto pra trabalhar no seu projeto em um ambiente dedicado.

### Instalando o TA-Lib
Para instalar o TA-Lib no Windows, acesse [biblioteca TA-Lib não-oficial para Windows](https://www.lfd.uci.edu/~gohlke/pythonlibs/) e baixe a versão aplicável para a sua instalação do Python. Como menciono a versão 3.8.6 do Python no início do passo-a-passo, baixarei o arquivo TA_Lib‑0.4.19‑cp38‑cp38‑win_amd64.whl. Há também a versão 32-bits, caso seja o caso.

Execute `pip install FILE` para instalar. Substitua `FILE` pelo arquivo baixado, incluindo a extensão `.whl` no nome do arquivo.

Se você está no Linux/MacOS, cheque [os guias oficiais de instalação](https://mrjbq7.github.io/ta-lib/install.html).

### Instalando as demais bibliotecas requeridas
Para instalar as dependências do projeto, execute `pip install -r requirements.txt`. Esse último passo pode demorar alguns segundos.

# Conclusão
O projeto Watchtower iniciou em 2017, quando após concluir minha graduação em administração de empresas aprendi a programar. Contribuir para esse projeto tem sido uma grande oportunidade de aplicar duas disciplinas pelas quais sou apaixonado: finanças e programação.

*"No man is better than a machine. No machine is better than a man with a machine"*
Richard Bookstaber, MIT Economics Professor

Contato via hpdeandrade@gmail.com or [twitter](https://twitter.com/hpdeandrade).