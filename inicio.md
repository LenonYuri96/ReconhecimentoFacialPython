# Projeto de Reconhecimento Facial

Este projeto realiza o reconhecimento facial usando a biblioteca OpenCV em Python. O programa permite cadastrar novos usuários e realizar o reconhecimento facial em tempo real.

## Requisitos

- Python 3.x
- XAMPP para o MySQL
- OpenCV e outras dependências Python

## Passos para Testar o Projeto

### 1. Clone o Repositório

Clone o repositório do GitHub e navegue até o diretório do projeto:


git clone https://github.com/LYuri26/ReconhecimentoFacialPython.git
cd ReconhecimentoFacialPython


### 2. Configure o Ambiente Virtual

Crie e ative um ambiente virtual para gerenciar as dependências:


python3 -m venv venv
source venv/bin/activate


### 3. Instale as Dependências

Instale as dependências necessárias a partir do arquivo `requirements.txt`:


pip install -r requirements.txt


Instale `pyfiglet` separadamente, se não estiver incluído no `requirements.txt`:


pip install pyfiglet


### 4. Atualize os Pacotes (se necessário)

Se houver um script `update_packages.sh` para atualizar pacotes, torne-o executável e execute-o:


chmod +x update_packages.sh
./update_packages.sh


**Nota:** Se o comando `update_packages.sh` não estiver presente ou não for necessário, você pode ignorar esta etapa.

### 5. Configure o XAMPP

Certifique-se de que o XAMPP está configurado com as seguintes credenciais:

- **Usuário:** root
- **Senha:** (vazio)
- **Host:** localhost

Certifique-se de que o MySQL está em execução no XAMPP.

### 6. Prepare o Projeto

Certifique-se de que o arquivo `haarcascade_frontalface_default.xml` está no diretório raiz do projeto. Você pode baixá-lo do repositório OpenCV:

[Download Haar Cascade XML](https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml)

### 7. Execute o Projeto

Para iniciar o reconhecimento facial, execute o script `app.py`:


python app.py


### 8. Utilizando o Programa

Quando o programa iniciar, você terá as seguintes opções:

- **Opção 1:** Cadastrar um novo usuário
  - Insira o nome, CPF, e-mail e telefone do usuário.
  - O programa capturará e salvará fotos do rosto para treinamento.

- **Opção 2:** Realizar o reconhecimento facial
  - Se você tiver fotos suficientes para treinamento, o programa usará a câmera para reconhecer rostos.

### 9. Resolução de Problemas

Aqui estão algumas soluções para problemas comuns:

- **Erro `Qt platform plugin "wayland"`:**
  - Esse é um aviso que pode não afetar a funcionalidade do programa. Pode ser ignorado se o programa estiver funcionando.

- **Erro `Can't open file: 'haarcascade_frontalface_default.xml'`:**
  - Certifique-se de que o arquivo `haarcascade_frontalface_default.xml` está no diretório raiz do projeto.

- **Erro `Empty training data was given`:**
  - Certifique-se de que há pelo menos 2 fotos de treinamento por usuário.

- **Erro de permissão (`PermissionError: [Errno 13]`):**
  - Verifique se o diretório `USUARIO` e seus subdiretórios têm permissões adequadas.

## Contribuições

Se você deseja contribuir para o projeto, sinta-se à vontade para fazer um fork do repositório e enviar pull requests com suas melhorias.
