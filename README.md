Obs.: caso o app esteja no modo "sleeping" (dormindo) ao entrar, basta clicar no botão que estará disponível e aguardar, para ativar o mesmo. 
![print](https://github.com/user-attachments/assets/e221115c-2585-4825-aa4b-8d577b49612e)
# 🧠AWS Mind Map pro

O AWS Mind Map pro é um web app interativo construído com Python e Streamlit, projetado para ajudar alunos/usuários AWS a visualizar serviços da AWS e suas relações em um formato de mapa mental dinâmico. Os dados dos serviços são carregados a partir de um arquivo CSV, e os usuários podem interagir com o mapa, adicionar notas, salvar seu progresso e exportar o mapa mental como um documento PDF.

## ✨ Funcionalidades

* **Geração Dinâmica de Mapa Mental:** Carrega automaticamente dados de serviços AWS de um arquivo CSV localizado na raiz do projeto.
* **Mapeamento Inteligente de Colunas:** Tenta identificar automaticamente as colunas `Serviço`, `Categoria` e `Descrição` no CSV.
* **Nós Interativos:**
    * Arraste e solte nós para organizar o mapa.
    * Selecione nós para definir um "pai" para novos nós.
* **Navegação:**
    * Pan (arrastar o fundo) e Zoom (scroll do mouse) para fácil navegação.
    * Botão para resetar a visualização.
* **Visualização Aprimorada:**
    * Nós coloridos por categoria de serviço AWS.
    * Tooltips informativos exibindo nome, categoria e descrição ao passar o mouse sobre um nó.
* **Adição de Conteúdo:**
    * Adicione serviços individualmente a partir de uma lista suspensa.
    * Adicione todos os serviços de uma categoria específica.
    * Crie "Nós Customizados" para anotações ou itens não listados no CSV.
* **Gerenciamento de Nós:**
    * Apague nós selecionados (exceto o nó central AWS).
    * Limpe todo o mapa (restaurando apenas o nó central AWS).
* **Persistência:**
    * **Salvar Mapa:** Salve o estado atual do seu mapa mental (nós, posições, conexões) em um arquivo JSON.
    * **Carregar Mapa:** Carregue um mapa mental previamente salvo de um arquivo JSON para continuar o trabalho.
* **Exportação:**
    * Exporte o mapa mental visual para um arquivo PDF.
    * O PDF inclui uma imagem do mapa e uma seção detalhada com informações de cada nó presente.
* **Logo Personalizada:** Exibe automaticamente um logo da AWS no nó central se um arquivo de imagem (`awslogo.png`, `aws.svg`, etc.) for encontrado na pasta raiz.

## 🚀 Configuração e Instalação

1.  **Pré-requisitos:**
    * Python 3.8 ou superior.
    * pip (gerenciador de pacotes Python).

2.  **Clonar o Repositório (Opcional):**
    ```bash
    git clone <url-do-seu-repositorio>
    cd <nome-do-diretorio>
    ```

3.  **Instalar Dependências:**
    Crie um ambiente virtual (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```
    Instale as bibliotecas necessárias:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Preparar Arquivo de Dados CSV:**
    * O repositório já inclui o arquivo `services.csv` com os serviços AWS. Para usar dados próprios, substitua-o por outro CSV na pasta raiz do projeto.
    * **Colunas Mandatórias (ou variações que o app tentará mapear):**
        * `Nome do Servico` (ou `Service`, `Servico`)
        * `Categoria` (ou `Category`)
        * `Descricao` (ou `Description`, `Descric`)
    * **Codificação:** UTF-8.
    * O aplicativo carregará o primeiro arquivo `.csv` que encontrar na pasta raiz.

5.  **Logo da AWS:**
    * Para exibir um logo no nó central do mapa mental, coloque o arquivo de imagem na pasta raiz do projeto:
        `awslogo.png`

## 🏃 Como Executar

Após a configuração e instalação das dependências:

1.  Navegue até o diretório raiz do projeto no seu terminal.
2.  Execute o seguinte comando:
    ```bash
    streamlit run app.py
    ```
3.  A aplicação será aberta automaticamente no seu navegador web padrão.

### 🛠️ Estrutura de Arquivos Esperada

├── app.py                 # Script principal da aplicação Streamlit
├── services.csv           # Arquivo CSV com os dados dos serviços AWS
├── awslogo.png            # (Opcional) Imagem do logo da AWS
├── requirements.txt       # Dependências Python
└── README.md              # Este arquivo

#### Por Ary Ribeiro | aryribeiro@gmail.com