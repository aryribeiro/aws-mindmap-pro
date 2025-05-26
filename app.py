import streamlit as st
import pandas as pd
import base64
from pathlib import Path
import json

# Configuração da página
st.set_page_config(
    page_title="AWS MindMap - Mapa Mental",
    page_icon="🧠",
    layout="wide"
)

def load_csv_data():
    """Carrega automaticamente o CSV da pasta raiz"""
    try:
        csv_files = list(Path(".").glob("*.csv"))
        if csv_files:
            csv_file = csv_files[0]
            df = pd.read_csv(csv_file)

            column_mapping = {}
            for col in df.columns:
                col_lower_stripped = col.lower().strip().replace("ç", "c").replace("ã", "a")
                if 'nome do servico' == col_lower_stripped or 'service' == col_lower_stripped or 'servico' == col_lower_stripped:
                    column_mapping[col] = 'Service'
                elif 'categoria' == col_lower_stripped or 'category' == col_lower_stripped:
                    column_mapping[col] = 'Category'
                elif 'descricao' == col_lower_stripped or 'description' == col_lower_stripped or 'descric' in col_lower_stripped :
                    column_mapping[col] = 'Description'

            df = df.rename(columns=column_mapping)

            required_cols = ['Service', 'Category', 'Description']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"CSV deve conter as colunas: {missing_cols}. Encontradas: {list(df.columns)}")
                return pd.DataFrame(), ""

            df = df.dropna(subset=['Service']).drop_duplicates(subset=['Service'])
            df['Service'] = df['Service'].astype(str).str.strip()
            df = df[df['Service'] != '']

            df = df.fillna('')

            return df, csv_file.name
        else:
            st.error("Nenhum arquivo CSV encontrado na pasta raiz do projeto.")
            return pd.DataFrame(), ""
    except Exception as e:
        st.error(f"Erro ao carregar ou processar o CSV: {e}")
        return pd.DataFrame(), ""

def get_aws_logo_base64():
    """Converte a logo AWS para base64 e retorna base64 e extensão."""
    try:
        logo_names = ["awslogo.png", "aws-logo.png", "aws.png", "logo.png",
                     "awslogo.jpg", "aws-logo.jpg", "aws.jpg", "logo.jpg",
                     "awslogo.svg", "aws-logo.svg", "aws.svg", "logo.svg"]

        for logo_name in logo_names:
            logo_path = Path(logo_name)
            if logo_path.exists():
                with open(logo_path, "rb") as f:
                    logo_data = f.read()
                return base64.b64encode(logo_data).decode(), logo_path.suffix.lower()
        return None, None
    except Exception as e:
        st.error(f"Erro ao carregar logo: {e}")
        return None, None

def create_mindmap_html(df, csv_filename, logo_info_tuple):
    """Cria o HTML do mapa mental com dados do CSV"""

    services_data = df.to_dict('records')
    services_json = json.dumps(services_data)

    logo_base64_str, file_extension_str = logo_info_tuple if logo_info_tuple else (None, None)

    center_node_svg_string = ''
    if logo_base64_str:
        mime_type = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.svg': 'image/svg+xml'
        }.get(file_extension_str, 'image/png')

        center_node_svg_string = f'''<image id="awsCenterLogoImage" data-type="image" x="-40" y="-30" width="80" height="60" href="data:{mime_type};base64,{logo_base64_str}" preserveAspectRatio="xMidYMid meet" style="cursor: pointer;"/>'''
    else:
        center_node_svg_string = '''<text id="awsCenterLogoText" data-type="text" x="0" y="8" text-anchor="middle" fill="#232F3E" font-size="24" font-weight="bold" style="cursor: pointer;">AWS</text>'''

    center_node_svg_for_js = json.dumps(center_node_svg_string)

    html_content = f'''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AWS MindMap pro</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <style>
            body {{
                font-family: 'Amazon Ember', 'Helvetica Neue', sans-serif;
                margin: 0;
                padding: 0;
                background: #232F3E;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }}

            .container {{
                flex-grow: 1;
                background: white;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }}

            .header {{
                background: linear-gradient(135deg, #1a252f 0%, #FF9900 100%);
                padding: 15px 20px;
                color: white;
                text-align: center;
                border-bottom: 3px solid #FF9900;
            }}

            .header h1 {{
                margin: 0;
                font-size: 1.8rem;
                font-weight: 700;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }}

            .info-bar {{
                background: #f0f2f5;
                padding: 10px 15px;
                border-bottom: 1px solid #dee2e6;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
            }}

            .controls {{
                display: flex;
                gap: 8px;
                align-items: center;
                flex-wrap: wrap;
            }}

            select, .btn {{
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background: white;
                font-size: 14px;
                transition: all 0.2s ease-in-out;
            }}

            select {{
                min-width: 220px;
                max-width: 300px;
            }}
            select:focus {{
                border-color: #FF9900;
                box-shadow: 0 0 0 0.2rem rgba(255, 153, 0, 0.25);
                outline: none;
            }}

            .btn {{
                background: #FF9900;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: 500;
            }}
            .btn:hover:not(:disabled) {{
                background: #e68a00;
                transform: translateY(-1px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .btn:disabled {{
                background: #adb5bd;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }}
            .btn.danger {{ background: #dc3545; }}
            .btn.danger:hover {{ background: #c82333; }}
            .btn.delete-node {{ background-color: #d9534f; }}
            .btn.delete-node:hover {{ background-color: #c9302c; }}
            .btn.download-pdf {{ background: #007bff; }}
            .btn.download-pdf:hover {{ background: #0069d9; }}
            .btn.custom-node {{ background-color: #5cb85c; }}
            .btn.custom-node:hover {{ background-color: #4cae4c; }}
            .btn.save-map {{ background-color: #28a745; }} 
            .btn.save-map:hover {{ background-color: #218838; }}
            .btn.load-map {{ background-color: #fd7e14; }} 
            .btn.load-map:hover {{ background-color: #e66a00; }}


            .canvas-container {{
                flex-grow: 1;
                position: relative;
                /* overflow: hidden; // Managed by JS during PDF export */
                background: #f8f9fa;
            }}

            #mindMapCanvas {{
                width: 100%;
                height: 100%;
                cursor: grab;
                background-image: radial-gradient(circle, #e9ecef 1px, transparent 1px);
                background-size: 20px 20px;
            }}
            #mindMapCanvas:active {{ cursor: grabbing; }}

            .stats {{ display: flex; gap: 15px; font-size: 14px; color: #495057; }}
            .stat-item {{ display: flex; align-items: center; gap: 5px; }}
            .stat-item strong {{ color: #232F3E; }}

            .notification {{
                position: fixed; top: 20px; right: 20px;
                background: #28a745; color: white; padding: 12px 20px;
                border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateX(calc(100% + 30px)); opacity: 0;
                transition: transform 0.4s ease, opacity 0.4s ease;
                z-index: 2000; max-width: 300px;
            }}
            .notification.show {{ transform: translateX(0); opacity: 1; }}
            .notification.error {{ background: #dc3545; }}
            .notification.warning {{ background: #ffc107; color: #333; }}


            .tooltip {{
                position: absolute; background: rgba(35, 47, 62, 0.95);
                color: white; padding: 10px 15px; border-radius: 6px;
                font-size: 13px; pointer-events: none; z-index: 1000;
                max-width: 320px; line-height: 1.5; border: 1px solid #FF9900;
                box-shadow: 0 3px 8px rgba(0,0,0,0.2);
            }}
            .node.selected > rect, .central-node.selected > image, .central-node.selected > text {{
                filter: drop-shadow(0px 0px 5px #FF9900) drop-shadow(0px 0px 10px #FF9900);
            }}
            .service-node.selected > rect {{
                stroke: #FF9900 !important;
                stroke-width: 3px !important;
            }}

        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 AWS MindMap pro - Mapa Mental</h1>
            </div>

            <div class="info-bar">
                <div class="controls">
                    <select id="serviceSelect">
                        <option value="">Selecione um serviço AWS...</option>
                    </select>
                    <button id="addService" class="btn" disabled>➕Adicionar</button>
                    <button id="addCustomNode" class="btn custom-node">✏️Nó Customizado</button>
                    <button id="addByCategory" class="btn" style="background-color: #6f42c1;">📦Adicionar por Categoria</button>
                    <button id="saveWorkBtn" class="btn save-map">💾Salvar</button>
                    <button id="loadWorkBtn" class="btn load-map">📂Carregar</button>
                    <input type="file" id="loadMapInput" accept=".json" style="display: none;">
                    
                    <button id="deleteSelectedNode" class="btn delete-node">🗑️Apagar Selecionado</button>
                    <button id="downloadPDF" class="btn download-pdf">📄PDF</button>
                    <button id="clearAll" class="btn danger">🧹Limpar Tela</button>
                    <button id="resetView" class="btn" style="background-color: #6c757d;">🔄Centralizar</button>
                </div>
                <div class="stats">
                    <div class="stat-item"><span>Nós:</span><strong id="totalServices">0</strong></div>
                    <div class="stat-item"><span>Categorias no Mapa:</span><strong id="totalCategories">0</strong></div>
                </div>
            </div>

            <div class="canvas-container">
                <svg id="mindMapCanvas">
                    <defs>
                        <filter id="nodeShadow" x="-50%" y="-50%" width="200%" height="200%">
                            <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.2"/>
                        </filter>
                        <marker id="arrowhead" markerWidth="10" markerHeight="7"
                                refX="9" refY="3.5" orient="auto" fill="#546E7A">
                            <polygon points="0 0, 10 3.5, 0 7"/>
                        </marker>
                    </defs>
                    <g id="edgesGroup"></g>
                    <g id="nodesGroup"></g>
                </svg>
            </div>
        </div>

        <div id="notification" class="notification"></div>
        <div id="tooltip" class="tooltip" style="display: none;"></div>

        <script>
            const rawCsvData = {services_json};
            const AWS_CENTER_ID = 'aws_central_logo_node';

            let _resolvedCenterNodeSvgContent;
            const actualSvgStringFromPython = {center_node_svg_for_js};

            if (typeof actualSvgStringFromPython === 'string' && actualSvgStringFromPython.trim() !== '') {{
                _resolvedCenterNodeSvgContent = actualSvgStringFromPython;
            }} else {{
                console.warn("[MINDMAP WARN] Conteúdo da logo do Python não é uma string SVG válida ou está vazia. Conteúdo:", actualSvgStringFromPython, ". Usando fallback.");
                _resolvedCenterNodeSvgContent = '<text id="awsCenterLogoText_Fallback" data-type="text" x="0" y="8" text-anchor="middle" fill="#232F3E" font-size="24" font-weight="bold" style="cursor: pointer;">AWS (FB)</text>';
            }}
            const centerNodeSvgContentFromPython = _resolvedCenterNodeSvgContent;


            class AWSMindMapPro {{
                constructor() {{
                    this.csvData = rawCsvData;
                    this.canvas = document.getElementById('mindMapCanvas');
                    this.nodesG = document.getElementById('nodesGroup');
                    this.edgesG = document.getElementById('edgesGroup');

                    this.serviceSelect = document.getElementById('serviceSelect');
                    this.addBtn = document.getElementById('addService');
                    this.addCustomNodeBtn = document.getElementById('addCustomNode');
                    this.addCategoryBtn = document.getElementById('addByCategory');
                    this.saveWorkBtn = document.getElementById('saveWorkBtn');
                    this.loadWorkBtn = document.getElementById('loadWorkBtn');
                    this.loadMapInput = document.getElementById('loadMapInput');

                    this.deleteSelectedNodeBtn = document.getElementById('deleteSelectedNode');
                    this.clearBtn = document.getElementById('clearAll');
                    this.resetBtn = document.getElementById('resetView');
                    this.downloadPDFBtn = document.getElementById('downloadPDF');

                    this.notification = document.getElementById('notification');
                    this.tooltip = document.getElementById('tooltip');

                    this.nodes = new Map();
                    this.edges = new Map();

                    this.centerX = 800;
                    this.centerY = 400;

                    this.initialViewBox = {{ x: 0, y: 0, width: 1600, height: 800 }};
                    this.currentViewBox = {{ ...this.initialViewBox }};
                    this.canvas.setAttribute('viewBox', `0 0 1600 800`);

                    this.categoryColors = {{
                        'Machine Learning': '#8E44AD',
                        'Suporte ao Desenvolvedor': '#3498DB',
                        'Ferramentas de Desenvolvedor': '#2ECC71',
                        'Computação': '#E74C3C',
                        'Rede e Entrega de Conteúdo': '#F39C12',
                        'Migração e Transferência': '#9B59B6',
                        'Gerenciamento e Governança': '#34495E',
                        'Segurança e Identidade': '#E67E22',
                        'Conformidade': '#1ABC9C',
                        'Armazenamento': '#D35400',
                        'Integração de Aplicações': '#16A085',
                        'Banco de Dados': '#27AE60',
                        'Analytics': '#7D3C98',
                        'IoT': '#FF6B35',
                        'Blockchain': '#6C5CE7',
                        'Quantum': '#A29BFE',
                        'Containers': '#00B894',
                        'Serverless': '#FDCB6E',
                        'Mobile': '#E17055',
                        'Custom Notes': '#A6B1E1',
                        'Anotações': '#A6B1E1',
                        'Observações': '#A6B1E1',
                        'Outros': '#7F8C8D'
                    }};

                    this.selectedNodeId = AWS_CENTER_ID;
                    this.draggedNode = null;
                    this.draggedNodeOffsetX = 0;
                    this.draggedNodeOffsetY = 0;
                    this.isPanning = false;
                    this.panStartX = 0;
                    this.panStartY = 0;

                    this.init();
                }}

                init() {{
                    this.populateServiceSelect();
                    this.initEventListeners();
                    this.initPanAndZoom();
                    this.addCentralAWSNode();
                    if (this.nodes.has(AWS_CENTER_ID)) {{ // Select central node after it's added
                        this.selectNode(AWS_CENTER_ID);
                    }}
                    this.updateStats();
                }}

                addCentralAWSNode() {{
                    // Check if central node already exists from a load operation perhaps
                    if (this.nodes.has(AWS_CENTER_ID)) {{
                        const existingCentral = this.nodes.get(AWS_CENTER_ID);
                        this.renderNode(existingCentral); // Re-render if needed
                        return;
                    }}
                    const awsNodeData = {{
                        id: AWS_CENTER_ID,
                        name: 'AWS',
                        category: 'Central',
                        description: 'Amazon Web Services',
                        x: this.centerX,
                        y: this.centerY,
                        isCentral: true,
                        parentId: null
                    }};
                    this.nodes.set(AWS_CENTER_ID, awsNodeData);
                    this.renderNode(awsNodeData);
                }}

                populateServiceSelect() {{
                    this.serviceSelect.innerHTML = '<option value="">Selecione um serviço AWS...</option>';
                    const categories = {{}};
                    this.csvData.forEach(service => {{
                        const category = service.Category || 'Outros';
                        if (!categories[category]) categories[category] = [];
                        categories[category].push(service);
                    }});

                    Object.keys(categories).sort().forEach(category => {{
                        const optgroup = document.createElement('optgroup');
                        optgroup.label = `${{category}} (${{categories[category].length}})`;
                        categories[category].sort((a, b) => a.Service.localeCompare(b.Service)).forEach(service => {{
                            const option = document.createElement('option');
                            option.value = service.Service;
                            option.textContent = service.Service;
                            optgroup.appendChild(option);
                        }});
                        this.serviceSelect.appendChild(optgroup);
                    }});
                }}

                initEventListeners() {{
                    this.addBtn.addEventListener('click', () => this.addSelectedService());
                    this.addCustomNodeBtn.addEventListener('click', () => this.promptForCustomNode());
                    this.addCategoryBtn.addEventListener('click', () => this.promptAddByCategory());
                    
                    this.saveWorkBtn.addEventListener('click', () => this.saveMindMapState());
                    this.loadWorkBtn.addEventListener('click', () => this.loadMapInput.click());
                    this.loadMapInput.addEventListener('change', (event) => this.handleFileLoad(event));

                    this.deleteSelectedNodeBtn.addEventListener('click', () => this.deleteSelectedNode());
                    this.clearBtn.addEventListener('click', () => this.clearAllNodes());
                    this.resetBtn.addEventListener('click', () => this.resetView());
                    this.downloadPDFBtn.addEventListener('click', () => this.downloadPDF());

                    this.serviceSelect.addEventListener('change', () => {{
                        this.addBtn.disabled = !this.serviceSelect.value;
                    }});

                    this.nodesG.addEventListener('mousedown', (e) => {{
                        const targetNodeElement = e.target.closest('.node');
                        if (targetNodeElement) {{
                            e.stopPropagation();
                            this.draggedNode = this.nodes.get(targetNodeElement.id);
                            if (!this.draggedNode) return;

                            this.selectNode(this.draggedNode.id);

                            const CTM = this.canvas.getScreenCTM().inverse();
                            const mousePos = this.getMousePosition(e, CTM);

                            this.draggedNodeOffsetX = this.draggedNode.x - mousePos.x;
                            this.draggedNodeOffsetY = this.draggedNode.y - mousePos.y;
                            this.canvas.style.cursor = 'grabbing';
                        }}
                    }});

                    this.canvas.addEventListener('mousedown', (e) => {{
                        if (!e.target.closest('.node')) {{
                            this.isPanning = true;
                            this.panStartX = e.clientX;
                            this.panStartY = e.clientY;
                            this.canvas.style.cursor = 'grabbing';
                        }}
                    }});

                    this.canvas.addEventListener('mousemove', (e) => {{
                        if (this.draggedNode) {{
                            e.preventDefault();
                            const CTM = this.canvas.getScreenCTM().inverse();
                            const mousePos = this.getMousePosition(e, CTM);

                            this.draggedNode.x = mousePos.x + this.draggedNodeOffsetX;
                            this.draggedNode.y = mousePos.y + this.draggedNodeOffsetY;

                            this.updateNodePosition(this.draggedNode);
                            this.updateConnectedEdges(this.draggedNode.id);
                        }} else if (this.isPanning) {{
                            e.preventDefault();
                            const dx = (this.panStartX - e.clientX) * (this.currentViewBox.width / this.canvas.clientWidth);
                            const dy = (this.panStartY - e.clientY) * (this.currentViewBox.height / this.canvas.clientHeight);
                            this.currentViewBox.x += dx;
                            this.currentViewBox.y += dy;
                            this.updateViewBoxAttribute();
                            this.panStartX = e.clientX;
                            this.panStartY = e.clientY;
                        }}
                    }});

                    this.canvas.addEventListener('mouseup', () => {{
                        if (this.draggedNode) {{
                            this.draggedNode = null;
                            this.canvas.style.cursor = 'grab';
                        }}
                        if (this.isPanning) {{
                            this.isPanning = false;
                            this.canvas.style.cursor = 'grab';
                        }}
                    }});
                     this.canvas.addEventListener('mouseleave', () => {{
                        if (this.draggedNode) {{
                            this.draggedNode = null;
                             this.canvas.style.cursor = 'grab';
                        }}
                        if (this.isPanning) {{
                            this.isPanning = false;
                            this.canvas.style.cursor = 'grab';
                        }}
                    }});
                }}

                getMousePosition(evt, CTM) {{
                    const pt = this.canvas.createSVGPoint();
                    pt.x = evt.clientX;
                    pt.y = evt.clientY;
                    return pt.matrixTransform(CTM);
                }}

                initPanAndZoom() {{
                    this.canvas.addEventListener('wheel', (e) => {{
                        e.preventDefault();
                        const CTM = this.canvas.getScreenCTM().inverse();
                        const mousePos = this.getMousePosition(e, CTM);

                        const scaleFactor = e.deltaY > 0 ? 1.1 : 0.9;

                        this.currentViewBox.x = mousePos.x - (mousePos.x - this.currentViewBox.x) * scaleFactor;
                        this.currentViewBox.y = mousePos.y - (mousePos.y - this.currentViewBox.y) * scaleFactor;
                        this.currentViewBox.width *= scaleFactor;
                        this.currentViewBox.height *= scaleFactor;
                        this.updateViewBoxAttribute();
                    }});
                }}

                selectNode(nodeId) {{
                    if (this.selectedNodeId && this.nodes.has(this.selectedNodeId)) {{
                        const oldSelectedElem = document.getElementById(this.selectedNodeId);
                        if(oldSelectedElem) oldSelectedElem.classList.remove('selected');
                    }}
                    this.selectedNodeId = nodeId;
                    const newSelectedElem = document.getElementById(nodeId);
                    if (newSelectedElem) {{
                        newSelectedElem.classList.add('selected');
                    }}
                }}

                promptAddByCategory() {{
                    const uniqueCategories = [...new Set(this.csvData.map(s => s.Category || 'Outros'))].sort();
                    const promptMessage = "Selecione a categoria para adicionar:\\n\\n" +
                                        uniqueCategories.map((c, i) => `${{i + 1}}. ${{c}}`).join('\\n') +
                                        "\\n\\nDigite o número ou o nome da categoria:";
                    const input = prompt(promptMessage);
                    if (!input) return;

                    let chosenCategory;
                    const inputNum = parseInt(input);
                    if (!isNaN(inputNum) && inputNum > 0 && inputNum <= uniqueCategories.length) {{
                        chosenCategory = uniqueCategories[inputNum - 1];
                    }} else {{
                        chosenCategory = uniqueCategories.find(c => c.toLowerCase().includes(input.toLowerCase()));
                    }}

                    if (chosenCategory) {{
                        this.addServicesByCategory(chosenCategory);
                    }} else {{
                        this.showNotification(`Categoria "${{input}}" não encontrada.`, 'error');
                    }}
                }}

                promptForCustomNode() {{
                    const name = prompt("Nome do Serviço/Nó Customizado:", "Minha Anotação");
                    if (!name || name.trim() === "") {{
                        this.showNotification("Nome do nó não pode ser vazio.", "warning");
                        return;
                    }}

                    if (this.nodes.has(name.trim())) {{
                        this.showNotification(`Nó com nome "${{name.trim()}}" já existe. Escolha outro nome.`, "error");
                        return;
                    }}

                    const category = prompt("Categoria (ex: Anotações, Observações):", "Custom Notes");
                     if (!category || category.trim() === "") {{
                        this.showNotification("Categoria não pode ser vazia.", "warning");
                        return;
                    }}
                    const description = prompt("Descrição/Detalhes:", "");

                    const serviceData = {{
                        Service: name.trim(),
                        Category: category.trim(),
                        Description: description.trim(),
                        isCustom: true
                    }};

                    const parentId = this.selectedNodeId || AWS_CENTER_ID;
                    this.addNode(serviceData, parentId);
                    this.showNotification(`Nó customizado "${{name.trim()}}" adicionado.`, "success");
                }}


                addServicesByCategory(category) {{
                    const parentId = this.selectedNodeId || AWS_CENTER_ID;
                    const servicesToAdd = this.csvData.filter(s => (s.Category || 'Outros') === category);
                    let count = 0;
                    servicesToAdd.forEach(serviceData => {{
                        if (!this.nodes.has(serviceData.Service)) {{
                           this.addNode(serviceData, parentId);
                           count++;
                        }}
                    }});
                    if (count > 0) {{
                        this.showNotification(`${{count}} serviços da categoria "${{category}}" adicionados.`, 'success');
                    }} else {{
                        this.showNotification(`Nenhum novo serviço de "${{category}}" para adicionar.`, 'info');
                    }}
                }}

                addSelectedService() {{
                    const serviceName = this.serviceSelect.value;
                    if (!serviceName) return;
                    if (this.nodes.has(serviceName)) {{
                        this.showNotification(`Serviço "${{serviceName}}" já está no mapa.`, 'warning');
                        return;
                    }}
                    const serviceData = this.csvData.find(s => s.Service === serviceName);
                    if (serviceData) {{
                        const parentId = this.selectedNodeId || AWS_CENTER_ID;
                        this.addNode(serviceData, parentId);
                        this.showNotification(`"${{serviceName}}" adicionado.`, 'success');
                        this.serviceSelect.value = '';
                        this.addBtn.disabled = true;
                    }}
                }}

                addNode(serviceData, parentId) {{
                    let currentParentNode = this.nodes.get(parentId);
                     if (!currentParentNode) {{
                        console.warn(`Nó pai com ID "${{parentId}}" não encontrado. Usando nó central AWS como pai.`);
                        parentId = AWS_CENTER_ID;
                        currentParentNode = this.nodes.get(AWS_CENTER_ID);
                        if (!currentParentNode) {{
                           this.showNotification("Erro crítico: Nó central AWS não encontrado.", "error");
                           return;
                        }}
                    }}

                    const childrenOfParent = Array.from(this.nodes.values()).filter(n => n.parentId === parentId);
                    const angleIncrement = Math.PI / 6; 
                    const baseRadius = currentParentNode.isCentral ? 180 : 120;
                    const angle = childrenOfParent.length * angleIncrement + (currentParentNode.isCentral ? 0 : Math.random() * 0.1);

                    const x = currentParentNode.x + Math.cos(angle) * (baseRadius + Math.random() * 30);
                    const y = currentParentNode.y + Math.sin(angle) * (baseRadius + Math.random() * 30);

                    const newNodeData = {{
                        id: serviceData.Service,
                        name: serviceData.Service,
                        category: serviceData.Category || 'Outros',
                        description: serviceData.Description || (serviceData.isCustom ? 'Nó customizado' : 'Serviço AWS'),
                        x: x,
                        y: y,
                        parentId: parentId,
                        isCentral: false,
                        isCustom: serviceData.isCustom || false
                    }};

                    this.nodes.set(newNodeData.id, newNodeData);
                    this.renderNode(newNodeData);
                    if (parentId && parentId !== newNodeData.id) {{
                        this.addEdge(parentId, newNodeData.id);
                    }}
                    this.updateStats();
                }}

                _parseSvgStringAttributes(svgString) {{
                    const attrs = {{}};
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(`<svg xmlns="http://www.w3.org/2000/svg">${{svgString}}</svg>`, "image/svg+xml");
                    const element = doc.documentElement.firstChild;

                    if (element && element.attributes) {{
                        for (let i = 0; i < element.attributes.length; i++) {{
                            const attr = element.attributes[i];
                            attrs[attr.name] = attr.value;
                        }}
                        attrs.dataType = element.getAttribute('data-type') || element.nodeName.toLowerCase();
                        if (element.textContent) {{
                            attrs.textContent = element.textContent;
                        }}
                    }} else {{
                        console.warn("[MINDMAP PARSE_ATTR] Não foi possível parsear elemento SVG da string:", svgString);
                        attrs.dataType = 'error';
                    }}
                    return attrs;
                }}

                renderNode(nodeData) {{
                    let group = document.getElementById(nodeData.id);
                    if (!group) {{
                        group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                        group.setAttribute('id', nodeData.id);
                        this.nodesG.appendChild(group); 
                    }} else {{
                        while (group.firstChild) {{
                            group.removeChild(group.firstChild);
                        }}
                    }}
                    
                    group.setAttribute('class', 'node' + (nodeData.isCentral ? ' central-node' : ' service-node'));
                    group.setAttribute('transform', `translate(${{nodeData.x}}, ${{nodeData.y}})`);
                    group.style.cursor = 'pointer';

                    if (nodeData.isCentral) {{
                        // ... (código de renderização do nó central - permanece o mesmo) ...
                        if (centerNodeSvgContentFromPython && typeof centerNodeSvgContentFromPython === 'string' && centerNodeSvgContentFromPython.trim() !== "") {{
                            const attrs = this._parseSvgStringAttributes(centerNodeSvgContentFromPython);
                            let centralElement;

                            if (attrs.dataType === 'image') {{
                                centralElement = document.createElementNS('http://www.w3.org/2000/svg', 'image');
                                centralElement.setAttribute('id', attrs.id || 'awsCenterLogoImageJS');
                                centralElement.setAttribute('x', attrs.x || '-40');
                                centralElement.setAttribute('y', attrs.y || '-30');
                                centralElement.setAttribute('width', attrs.width || '80');
                                centralElement.setAttribute('height', attrs.height || '60');
                                if (attrs.href) centralElement.setAttributeNS('http://www.w3.org/1999/xlink', 'href', attrs.href);
                                centralElement.setAttribute('preserveAspectRatio', attrs.preserveAspectRatio || 'xMidYMid meet');
                            }} else if (attrs.dataType === 'text') {{
                                centralElement = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                                centralElement.setAttribute('id', attrs.id || 'awsCenterLogoTextJS');
                                centralElement.setAttribute('x', attrs.x || '0');
                                centralElement.setAttribute('y', attrs.y || '8');
                                centralElement.setAttribute('text-anchor', attrs['text-anchor'] || 'middle');
                                centralElement.setAttribute('fill', attrs.fill || '#232F3E');
                                centralElement.setAttribute('font-size', attrs['font-size'] || '24');
                                centralElement.setAttribute('font-weight', attrs['font-weight'] || 'bold');
                                centralElement.textContent = attrs.textContent || 'AWS (ErrParse)';
                            }}
                            if(centralElement) {{
                                centralElement.style.cursor = 'pointer';
                                group.appendChild(centralElement);
                            }} else {{
                                this.addJSFallbackCentralNodeContent(group, "Fallback: Element Creation");
                            }}
                        }} else {{
                            this.addJSFallbackCentralNodeContent(group, "Fallback: Invalid SVG Content");
                        }}
                    }} else {{ // Nós de serviço
                        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                        const textEl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                        
                        const fullNodeName = nodeData.name;
                        const fontSize = 13; 
                        const charWidthMultiplier = 7; // Estimativa de pixels por caracter
                        const internalPadding = 20; // Espaçamento interno total (horizontal) para o texto

                        let idealRectWidth = (fullNodeName.length * charWidthMultiplier) + internalPadding;

                        const minNodeWidth = 100;
                        const maxNodeWidth = 350; // Aumentado para nomes mais longos

                        let finalRectWidth = Math.max(minNodeWidth, idealRectWidth);
                        finalRectWidth = Math.min(finalRectWidth, maxNodeWidth);

                        const rectHeight = 40; 

                        let displayText = fullNodeName;
                        const maxCharsInFinalRect = Math.floor((finalRectWidth - internalPadding) / charWidthMultiplier);

                        if (fullNodeName.length > maxCharsInFinalRect && maxCharsInFinalRect > 0) {{
                            if (maxCharsInFinalRect <= 3) {{ // Muito pouco espaço, mostrar reticências ou 1-2 chars
                                displayText = fullNodeName.substring(0, maxCharsInFinalRect) + "..";
                            }} else {{
                                displayText = fullNodeName.substring(0, maxCharsInFinalRect - 3) + "...";
                            }}
                        }} else if (maxCharsInFinalRect <= 0 && fullNodeName.length > 0) {{
                             displayText = "..."; // Nenhum espaço para texto
                        }}
                        
                        if (displayText.replace(/\./g, '').length === 0 && fullNodeName.length > 0) {{
                           displayText = fullNodeName.substring(0,1) + (fullNodeName.length > 1 ? "..." : "");
                        }}


                        rect.setAttribute('x', -finalRectWidth / 2);
                        rect.setAttribute('y', -rectHeight / 2);
                        rect.setAttribute('width', finalRectWidth);
                        rect.setAttribute('height', rectHeight);
                        rect.setAttribute('rx', 6);
                        rect.setAttribute('ry', 6);
                        rect.setAttribute('fill', this.categoryColors[nodeData.category] || this.categoryColors['Outros']);
                        rect.setAttribute('stroke', '#333');
                        rect.setAttribute('stroke-width', 1.5);
                        rect.setAttribute('filter', 'url(#nodeShadow)');
                        
                        textEl.setAttribute('x', 0);
                        textEl.setAttribute('y', 5); 
                        textEl.setAttribute('text-anchor', 'middle');
                        textEl.setAttribute('fill', 'white');
                        textEl.setAttribute('font-size', fontSize + 'px');
                        textEl.setAttribute('font-weight', '600');
                        textEl.textContent = displayText;
                        
                        group.appendChild(rect);
                        group.appendChild(textEl);
                    }}
                    
                    const newGroup = group.cloneNode(true); 
                    group.parentNode.replaceChild(newGroup, group);
                    group = newGroup; 

                    group.addEventListener('mouseenter', (e) => this.showTooltip(e, nodeData));
                    group.addEventListener('mouseleave', () => this.hideTooltip());
                    group.addEventListener('mousemove', (e) => this.updateTooltipPosition(e));
                    group.addEventListener('click', (e) => {{
                        e.stopPropagation();
                        this.selectNode(nodeData.id);
                    }});
                }}

                addJSFallbackCentralNodeContent(groupElement, reason = "Generic Fallback") {{
                    while (groupElement.firstChild) {{
                        groupElement.removeChild(groupElement.firstChild);
                    }}
                    const fallbackText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    fallbackText.setAttribute('id', 'awsCenterLogoText_JS_Fallback');
                    fallbackText.setAttribute('x', '0');
                    fallbackText.setAttribute('y', '8');
                    fallbackText.setAttribute('text-anchor', 'middle');
                    fallbackText.setAttribute('fill', '#232F3E');
                    fallbackText.setAttribute('font-size', '24');
                    fallbackText.setAttribute('font-weight', 'bold');
                    fallbackText.style.cursor = 'pointer';
                    fallbackText.textContent = 'AWS (FB)';
                    groupElement.appendChild(fallbackText);
                    console.log(`[MINDMAP DEBUG] Fallback JS para conteúdo do nó central foi adicionado. Razão: ${{reason}}`);
                }}

                deleteSelectedNode() {{
                    if (!this.selectedNodeId || this.selectedNodeId === AWS_CENTER_ID) {{
                        this.showNotification("Selecione um nó para apagar. O nó central AWS não pode ser apagado.", "warning");
                        return;
                    }}

                    const nodeToDeleteData = this.nodes.get(this.selectedNodeId);
                    if (!nodeToDeleteData) {{
                        this.showNotification("Nó selecionado não encontrado.", "error");
                        this.selectedNodeId = AWS_CENTER_ID; 
                        this.selectNode(AWS_CENTER_ID);
                        return;
                    }}

                    if (!confirm(`Tem certeza que deseja apagar o nó "${{nodeToDeleteData.name}}"? Filhos serão ligados ao nó AWS.`)) {{
                        return;
                    }}

                    const nodeIdToDelete = this.selectedNodeId;

                    const nodeElement = document.getElementById(nodeIdToDelete);
                    if (nodeElement) nodeElement.remove();

                    const edgesToRemove = [];
                    this.edges.forEach((edge, edgeId) => {{
                        if (edge.source === nodeIdToDelete || edge.target === nodeIdToDelete) {{
                            edgesToRemove.push(edgeId);
                            document.getElementById(edgeId)?.remove();
                        }}
                    }});
                    edgesToRemove.forEach(edgeId => this.edges.delete(edgeId));

                    this.nodes.forEach(node => {{
                        if (node.parentId === nodeIdToDelete) {{
                            node.parentId = AWS_CENTER_ID;
                            this.addEdge(AWS_CENTER_ID, node.id);
                        }}
                    }});

                    this.nodes.delete(nodeIdToDelete);

                    this.showNotification(`Nó "${{nodeToDeleteData.name}}" apagado.`, "success");
                    this.selectedNodeId = AWS_CENTER_ID;
                    this.selectNode(AWS_CENTER_ID);
                    this.updateStats();
                }}


                updateNodePosition(nodeData) {{
                    const group = document.getElementById(nodeData.id);
                    if (group) {{
                        group.setAttribute('transform', `translate(${{nodeData.x}}, ${{nodeData.y}})`);
                    }}
                }}

                addEdge(sourceId, targetId) {{
                    const edgeId = `edge_${{sourceId}}_${{targetId}}`;
                    if (this.edges.has(edgeId) || sourceId === targetId) return;

                    const oldEdgeElement = document.getElementById(edgeId);
                    if (oldEdgeElement) oldEdgeElement.remove();
                    this.edges.delete(edgeId);


                    const edgeData = {{ id: edgeId, source: sourceId, target: targetId }};
                    this.edges.set(edgeId, edgeData);
                    this.renderEdge(edgeData);
                }}

                renderEdge(edgeData) {{
                    const sourceNode = this.nodes.get(edgeData.source);
                    const targetNode = this.nodes.get(edgeData.target);
                    if (!sourceNode || !targetNode) return;
                    
                    let line = document.getElementById(edgeData.id);
                    if (!line) {{
                        line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('id', edgeData.id);
                        this.edgesG.appendChild(line);
                    }}

                    const dx = targetNode.x - sourceNode.x;
                    const dy = targetNode.y - sourceNode.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);

                    const sourceGroup = document.getElementById(sourceNode.id);
                    let sourceRadius = sourceNode.isCentral ? 40 : 25;
                    if (sourceGroup && sourceGroup.firstChild && typeof sourceGroup.firstChild.getBBox === 'function') {{
                        try {{
                           const bbox = sourceGroup.firstChild.getBBox();
                           sourceRadius = Math.max(bbox.width, bbox.height) / 2 * 0.8; // 80% of max dimension
                        }} catch(e) {{ /* ignore error */ }}
                    }}
                    if (!sourceNode.isCentral && sourceGroup) {{
                        const rect = sourceGroup.querySelector('rect');
                        if (rect) sourceRadius = (parseFloat(rect.getAttribute('width')) || 100) / 2.2; // Ajustado
                    }}


                    const targetGroup = document.getElementById(targetNode.id);
                    let targetRadius = targetNode.isCentral ? 40 : 25;
                     if (!targetNode.isCentral && targetGroup) {{
                        const rect = targetGroup.querySelector('rect');
                        if (rect) targetRadius = (parseFloat(rect.getAttribute('width')) || 100) / 2.2; // Ajustado
                    }}

                    if (dist < (sourceRadius + targetRadius) || dist < 10 ) {{ // Aumentar distância mínima
                        if (line.parentNode) line.remove(); 
                        this.edges.delete(edgeData.id);
                        return; 
                    }}

                    line.setAttribute('x1', sourceNode.x + (dx * sourceRadius / dist) );
                    line.setAttribute('y1', sourceNode.y + (dy * sourceRadius / dist) );
                    line.setAttribute('x2', targetNode.x - (dx * targetRadius / dist) ); 
                    line.setAttribute('y2', targetNode.y - (dy * targetRadius / dist) ); 

                    line.setAttribute('stroke', '#546E7A');
                    line.setAttribute('stroke-width', 2);
                    line.setAttribute('marker-end', 'url(#arrowhead)');
                }}

                updateConnectedEdges(nodeId) {{
                    const edgesToRemove = [];
                    this.edges.forEach((edge, edgeId) => {{
                        if (edge.source === nodeId || edge.target === nodeId) {{
                            edgesToRemove.push(edgeId);
                            const edgeElement = document.getElementById(edgeId);
                            if (edgeElement) edgeElement.remove();
                        }}
                    }});
                    edgesToRemove.forEach(edgeId => this.edges.delete(edgeId));

                    const nodeData = this.nodes.get(nodeId);
                    if (nodeData && nodeData.parentId && this.nodes.has(nodeData.parentId)) {{
                        if (nodeData.id !== nodeData.parentId) {{ 
                           this.addEdge(nodeData.parentId, nodeId);
                        }}
                    }}
                    this.nodes.forEach(childNode => {{
                        if (childNode.parentId === nodeId) {{
                             if (childNode.id !== nodeId) {{ 
                                this.addEdge(nodeId, childNode.id);
                             }}
                        }}
                    }});
                }}

                clearAllNodes() {{
                    if (!confirm(`Limpar todos os nós (exceto AWS central)? O mapa atual será perdido.`)) return;

                    this.nodesG.innerHTML = ''; 
                    this.edgesG.innerHTML = ''; 
                    
                    this.nodes.clear();
                    this.edges.clear();
                    
                    this.addCentralAWSNode(); 
                    this.selectNode(AWS_CENTER_ID); 
                    this.updateStats();
                    this.showNotification('Mapa limpo. Nó central AWS restaurado.', 'success');
                }}

                updateViewBoxAttribute() {{
                    this.canvas.setAttribute('viewBox',
                        `${{this.currentViewBox.x}} ${{this.currentViewBox.y}} ${{this.currentViewBox.width}} ${{this.currentViewBox.height}}`);
                }}

                resetView() {{
                    this.currentViewBox = {{ ...this.initialViewBox }};
                    if (this.nodes.has(AWS_CENTER_ID)) {{
                        const centralNode = this.nodes.get(AWS_CENTER_ID);
                        this.currentViewBox.x = centralNode.x - this.initialViewBox.width / 2;
                        this.currentViewBox.y = centralNode.y - this.initialViewBox.height / 2;
                    }}
                    this.updateViewBoxAttribute();
                    this.showNotification('Visualização resetada!', 'success');
                }}

                updateStats() {{
                    const serviceNodesCount = Array.from(this.nodes.values()).filter(n => !n.isCentral).length;
                    const categoriesInMap = new Set(
                        Array.from(this.nodes.values())
                             .filter(n => !n.isCentral && n.category)
                             .map(s => s.category)
                    );
                    document.getElementById('totalServices').textContent = serviceNodesCount;
                    document.getElementById('totalCategories').textContent = categoriesInMap.size;
                }}

                showTooltip(event, nodeData) {{
                    if (nodeData.isCentral) return;
                    this.tooltip.innerHTML = `
                        <div style="font-weight: bold; margin-bottom: 8px; color: #FF9900;">${{nodeData.name}}</div>
                        <div style="margin-bottom: 6px;"><strong>Categoria:</strong> ${{nodeData.category}}</div>
                        <div><strong>Descrição:</strong> ${{nodeData.description || 'N/A'}}</div>
                    `;
                    this.tooltip.style.display = 'block';
                    this.updateTooltipPosition(event);
                }}
                updateTooltipPosition(event) {{
                    this.tooltip.style.left = (event.pageX + 15) + 'px';
                    this.tooltip.style.top = (event.pageY - 10) + 'px';
                }}
                hideTooltip() {{ this.tooltip.style.display = 'none'; }}

                showNotification(message, type = 'success') {{
                    this.notification.textContent = message;
                    this.notification.className = `notification ${{type}} show`;
                    setTimeout(() => {{ this.notification.classList.remove('show'); }}, 3500);
                }}

                saveMindMapState() {{
                    if (this.nodes.size === 0 ){{
                       this.showNotification("Mapa está vazio. Nada para salvar.", "info");
                       return;
                    }}
                    if (this.nodes.size === 1 && this.nodes.has(AWS_CENTER_ID)) {{
                        const values = Array.from(this.nodes.values());
                        const edges = Array.from(this.edges.values());
                        if (values.length === 1 && values[0].id === AWS_CENTER_ID && edges.length === 0) {{
                           this.showNotification("O mapa contém apenas o nó central AWS sem conexões. Adicione mais nós para salvar.", "info");
                           return;
                        }}
                    }}

                    const nodesArray = Array.from(this.nodes.values());
                    const dataToSave = {{
                        nodes: nodesArray,
                        viewBox: this.currentViewBox 
                    }};

                    const jsonString = JSON.stringify(dataToSave, null, 2);
                    const blob = new Blob([jsonString], {{ type: "application/json" }});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `aws-mindmap-estado-${{new Date().toISOString().slice(0,10).replace(/-/g,'')}}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    this.showNotification("Mapa salvo com sucesso!", "success");
                }}

                handleFileLoad(event) {{
                    const file = event.target.files[0];
                    if (!file) return;

                    if (file.type !== "application/json") {{
                        this.showNotification("Por favor, selecione um arquivo JSON (.json) válido.", "error");
                        event.target.value = null;
                        return;
                    }}

                    const reader = new FileReader();
                    reader.onload = (e) => {{
                        try {{
                            const fileContent = e.target.result;
                            const loadedData = JSON.parse(fileContent);

                            if (!loadedData.nodes || !Array.isArray(loadedData.nodes)) {{
                                throw new Error("Formato de nós inválido.");
                            }}
                            if (loadedData.nodes.length > 0) {{
                                const sampleNode = loadedData.nodes[0];
                                if (typeof sampleNode.id === 'undefined' ||
                                    typeof sampleNode.name === 'undefined' ||
                                    typeof sampleNode.x === 'undefined' ||
                                    typeof sampleNode.y === 'undefined' ) {{
                                    throw new Error("Dados dos nós incompletos.");
                                }}
                            }} 
                            
                            if (!confirm("Carregar este mapa? O mapa atual será substituído.")) {{
                                event.target.value = null;
                                return;
                            }}

                            this.loadMindMapState(loadedData);
                            this.showNotification("Mapa carregado com sucesso!", "success");

                        }} catch (err) {{
                            console.error("Erro ao carregar ou parsear o arquivo JSON:", err);
                            this.showNotification(`Erro ao carregar arquivo: ${{err.message}}`, "error");
                        }} finally {{
                            event.target.value = null; 
                        }}
                    }};
                    reader.onerror = () => {{
                        this.showNotification("Erro ao ler o arquivo.", "error");
                        event.target.value = null;
                    }};
                    reader.readAsText(file);
                }}

                loadMindMapState(loadedData) {{
                    this.nodesG.innerHTML = '';
                    this.edgesG.innerHTML = '';
                    this.nodes.clear();
                    this.edges.clear();
                    this.selectedNodeId = null;

                    let centralNodeIdToSelect = null;
                    let centralNodeDataFromLoad = null;

                    if (loadedData.nodes.length === 0) {{ // Se o arquivo JSON estiver vazio (sem nós)
                        this.addCentralAWSNode(); // Adiciona o nó central padrão
                        centralNodeIdToSelect = AWS_CENTER_ID;
                    }} else {{
                        loadedData.nodes.forEach(nodeData => {{
                            const newNode = {{ 
                                id: nodeData.id,
                                name: nodeData.name,
                                category: nodeData.category || (nodeData.isCentral ? 'Central' : 'Outros'),
                                description: nodeData.description || '',
                                x: parseFloat(nodeData.x) || this.centerX, // Default to current centerX if not present
                                y: parseFloat(nodeData.y) || this.centerY, // Default to current centerY if not present
                                parentId: nodeData.parentId || null,
                                isCentral: nodeData.isCentral || false, 
                                isCustom: nodeData.isCustom || false,
                            }};
                            if (newNode.id === AWS_CENTER_ID) {{
                                newNode.isCentral = true; 
                                centralNodeDataFromLoad = newNode;
                                this.centerX = newNode.x; 
                                this.centerY = newNode.y;
                            }}
                            this.nodes.set(newNode.id, newNode);
                        }});
                        
                        if (!centralNodeDataFromLoad) {{ 
                            console.warn(`[MINDMAP LOAD] Nó central padrão (ID: ${{AWS_CENTER_ID}}) não encontrado no arquivo. Adicionando um novo.`);
                            this.addCentralAWSNode(); 
                            centralNodeIdToSelect = AWS_CENTER_ID;
                        }} else {{
                            centralNodeIdToSelect = AWS_CENTER_ID;
                        }}
                    }}
                    
                    this.nodes.forEach(nodeData => {{
                        this.renderNode(nodeData);
                    }});

                    this.nodes.forEach(nodeData => {{
                        if (nodeData.parentId && this.nodes.has(nodeData.parentId) && nodeData.id !== nodeData.parentId) {{
                            this.addEdge(nodeData.parentId, nodeData.id);
                        }}
                    }});

                    this.updateStats();
                    if (centralNodeIdToSelect && this.nodes.has(centralNodeIdToSelect)) {{
                        this.selectNode(centralNodeIdToSelect);
                    }} else if (this.nodes.size > 0) {{
                        this.selectNode(this.nodes.keys().next().value);
                    }}

                    if (loadedData.viewBox) {{
                        this.currentViewBox = loadedData.viewBox;
                        this.updateViewBoxAttribute();
                    }} else {{
                         this.resetView(); 
                    }}
                }}


                async downloadPDF() {{
                    this.showNotification('Preparando PDF... Por favor, aguarde.', 'info');
                    const {{ jsPDF }} = window.jspdf;
                    const pdf = new jsPDF({{ orientation: 'landscape', unit: 'pt', format: 'a4' }});
                    
                    const svgElement = this.canvas;
                    const canvasContainer = svgElement.parentNode; 

                    const originalViewBox = svgElement.getAttribute('viewBox');
                    const originalSvgWidth = svgElement.style.width;
                    const originalSvgHeight = svgElement.style.height;
                    
                    const originalContainerWidth = canvasContainer.style.width;
                    const originalContainerHeight = canvasContainer.style.height;
                    const originalContainerOverflow = canvasContainer.style.overflow;

                    const defsElement = svgElement.querySelector('defs');
                    let defsParentNode = null;
                    let originalDefsNextSibling = null; 

                    if (defsElement) {{
                        defsParentNode = defsElement.parentNode;
                        originalDefsNextSibling = defsElement.nextSibling; 
                        defsParentNode.removeChild(defsElement); 
                    }}

                    try {{
                        pdf.setFontSize(20); 
                        pdf.setFont(undefined, 'bold');
                        const appTitle = "AWS MindMap pro";
                        const appTitleWidth = pdf.getTextDimensions(appTitle).w;
                        const pageWidthForTitle = pdf.internal.pageSize.getWidth();
                        pdf.text(appTitle, (pageWidthForTitle - appTitleWidth) / 2, 40);


                        if (this.nodes.size === 0) {{
                            this.showNotification('Nada para exportar no mapa.', 'warning');
                            return;
                        }}

                        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
                        let hasAnyContentToExport = false;

                        if (this.nodes.size === 1 && this.nodes.has(AWS_CENTER_ID)) {{
                            const centralElem = document.getElementById(AWS_CENTER_ID);
                            if (!centralElem || !centralElem.hasChildNodes()) {{
                                this.showNotification('Nó central não renderizado, nada para exportar.', 'warning');
                                return;
                            }}
                            minX = this.currentViewBox.x;
                            minY = this.currentViewBox.y;
                            maxX = this.currentViewBox.x + this.currentViewBox.width;
                            maxY = this.currentViewBox.y + this.currentViewBox.height;
                            hasAnyContentToExport = true;
                        }} else {{
                            this.nodes.forEach(node => {{
                                if (node.x !== undefined && node.y !== undefined) {{
                                    hasAnyContentToExport = true;
                                    const nodeElem = document.getElementById(node.id);
                                    let nodeWidth = 100; 
                                    let nodeHeight = 40; 

                                    if (node.isCentral) {{
                                        const centralChild = nodeElem ? nodeElem.firstChild : null;
                                        if (centralChild && typeof centralChild.getBBox === 'function') {{
                                            try {{
                                                const bbox = centralChild.getBBox();
                                                nodeWidth = bbox.width > 0 ? bbox.width : 80;
                                                nodeHeight = bbox.height > 0 ? bbox.height : 60;
                                            }} catch (e) {{ nodeWidth = 80; nodeHeight = 60; }}
                                        }} else {{ nodeWidth = 80; nodeHeight = 60; }}
                                    }} else {{ 
                                        const rect = nodeElem ? nodeElem.querySelector('rect') : null;
                                        if (rect) {{
                                            nodeWidth = parseFloat(rect.getAttribute('width')) || nodeWidth;
                                            nodeHeight = parseFloat(rect.getAttribute('height')) || nodeHeight;
                                        }} else {{ nodeWidth = 150; }} 
                                    }}
                                    minX = Math.min(minX, node.x - nodeWidth / 2 - 30); 
                                    minY = Math.min(minY, node.y - nodeHeight / 2 - 30);
                                    maxX = Math.max(maxX, node.x + nodeWidth / 2 + 30);
                                    maxY = Math.max(maxY, node.y + nodeHeight / 2 + 30);
                                }}
                            }});
                        }}

                        if (!hasAnyContentToExport) {{
                            this.showNotification('Nenhum conteúdo desenhável encontrado para exportar.', 'warning');
                            return;
                        }}

                        const contentWidth = Math.max(maxX - minX, 100);
                        const contentHeight = Math.max(maxY - minY, 100);
                        
                        svgElement.setAttribute('viewBox', `${{minX}} ${{minY}} ${{contentWidth}} ${{contentHeight}}`);
                        
                        const captureWidth = Math.max(contentWidth, 1200);
                        const captureHeight = (captureWidth / contentWidth) * contentHeight;
                        
                        svgElement.style.width = `${{captureWidth}}px`;
                        svgElement.style.height = `${{captureHeight}}px`;

                        canvasContainer.style.width = `${{captureWidth}}px`;
                        canvasContainer.style.height = `${{captureHeight}}px`;
                        canvasContainer.style.overflow = 'visible';


                        await new Promise(resolve => setTimeout(resolve, 450)); 

                        const canvasImage = await html2canvas(canvasContainer, {{ 
                            backgroundColor: '#f8f9fa',
                            scale: 1, 
                            useCORS: true,
                            logging: false, 
                            width: captureWidth,
                            height: captureHeight,
                            x: 0, 
                            y: 0, 
                            windowWidth: captureWidth, 
                            windowHeight: captureHeight 
                        }});

                        const imgData = canvasImage.toDataURL('image/png', 0.95);
                        const imgProps = pdf.getImageProperties(imgData);
                        
                        const titleAreaHeight = 60; 
                        const pdfPageContentWidth = pdf.internal.pageSize.getWidth() - 40; 
                        const pdfPageContentHeight = pdf.internal.pageSize.getHeight() - titleAreaHeight - 20;

                        const imgRatio = imgProps.width / imgProps.height;
                        let finalImgWidth = pdfPageContentWidth;
                        let finalImgHeight = pdfPageContentWidth / imgRatio;

                        if (finalImgHeight > pdfPageContentHeight) {{
                            finalImgHeight = pdfPageContentHeight;
                            finalImgWidth = pdfPageContentHeight * imgRatio;
                        }}
                        const xOffsetImage = (pdf.internal.pageSize.getWidth() - finalImgWidth) / 2;
                        let yOffsetImage = titleAreaHeight + (pdfPageContentHeight - finalImgHeight) / 2;
                        if (yOffsetImage < titleAreaHeight) yOffsetImage = titleAreaHeight;


                        pdf.addImage(imgData, 'PNG', xOffsetImage, yOffsetImage, finalImgWidth, finalImgHeight);

                        const serviceNodes = Array.from(this.nodes.values()).filter(n => !n.isCentral);
                        if (serviceNodes.length > 0) {{
                            pdf.addPage();
                            pdf.setFontSize(16);
                            pdf.setFont(undefined, 'bold');
                            pdf.text('Detalhes dos Nós no Mapa', 40, 50); 
                            
                            let yPos = 80;
                            pdf.setFontSize(10);

                            serviceNodes.sort((a,b) => a.name.localeCompare(b.name)).forEach(node => {{
                                const lineHeight = 12;
                                const blockSpacing = 15; 
                                const textMaxWidth = pdf.internal.pageSize.getWidth() - 80; 

                                if (yPos > pdf.internal.pageSize.getHeight() - 60) {{ 
                                    pdf.addPage();
                                    yPos = 50;
                                    pdf.setFontSize(16); 
                                    pdf.setFont(undefined, 'bold');
                                    pdf.text('Detalhes dos Nós no Mapa (continuação)', 40, yPos);
                                    yPos = 80;
                                    pdf.setFontSize(10);
                                }}
                                pdf.setFont(undefined, 'bold');
                                pdf.text(`Nó: ${{node.name}} ${{(node.isCustom ? "(Customizado)" : "")}}`, 40, yPos); 
                                yPos += lineHeight + 2;
                                
                                pdf.setFont(undefined, 'normal');
                                pdf.text(`Categoria: ${{node.category || 'N/A'}}`, 50, yPos);
                                yPos += lineHeight + 2;
                                
                                const descLines = pdf.splitTextToSize(`Descrição: ${{node.description || 'N/A'}}`, textMaxWidth);
                                pdf.text(descLines, 50, yPos);
                                yPos += descLines.length * lineHeight + blockSpacing; 
                            }});
                        }}
                        pdf.save(`aws-mindmap-pro-${{new Date().toISOString().slice(0,10).replace(/-/g,'')}}.pdf`);
                        this.showNotification('PDF gerado com sucesso!', 'success');

                    }} catch (error) {{
                        console.error("[MINDMAP PDF] Erro detalhado ao gerar PDF:", error);
                        this.showNotification(`Falha ao gerar PDF: ${{error.message || 'Erro desconhecido'}}`, 'error');
                    }} finally {{
                        if(originalViewBox) svgElement.setAttribute('viewBox', originalViewBox);
                        svgElement.style.width = originalSvgWidth || '100%';
                        svgElement.style.height = originalSvgHeight || '100%';
                        
                        canvasContainer.style.width = originalContainerWidth;
                        canvasContainer.style.height = originalContainerHeight;
                        canvasContainer.style.overflow = originalContainerOverflow;
                        
                        if (defsElement && defsParentNode) {{
                            if (originalDefsNextSibling) {{
                                defsParentNode.insertBefore(defsElement, originalDefsNextSibling);
                            }} else {{
                                defsParentNode.appendChild(defsElement);
                            }}
                        }}
                    }}
                }}
            }} // Fim da classe AWSMindMapPro

            document.addEventListener('DOMContentLoaded', () => {{
                try {{
                    window.awsMindMapInstance = new AWSMindMapPro();
                }} catch (e) {{
                    console.error("[MINDMAP ERRO FATAL] Erro ao instanciar AWSMindMapPro:", e);
                    const body = document.body || document.getElementsByTagName('body')[0];
                    if (body) {{
                        const errorDiv = document.createElement('div');
                        errorDiv.style.position = 'fixed'; errorDiv.style.top = '0'; errorDiv.style.left = '0';
                        errorDiv.style.width = '100%'; errorDiv.style.padding = '20px';
                        errorDiv.style.backgroundColor = 'rgba(255,0,0,0.9)'; errorDiv.style.color = 'white';
                        errorDiv.style.zIndex = '9999'; errorDiv.style.textAlign = 'center';
                        errorDiv.innerHTML = '<h1>Erro Crítico ao Carregar o App</h1><p>Verifique o console (F12). Problema ao processar dados iniciais.</p>';
                        const container = document.querySelector('.container');
                        if (container) {{ container.style.display = 'none'; }} 
                        body.prepend(errorDiv);
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    '''
    return html_content

app_logo_info = None 

def main():
    """Função principal da aplicação"""
    global app_logo_info

    df, csv_filename = load_csv_data()

    if df.empty:
        st.info("Por favor, adicione um arquivo CSV válido na pasta raiz para gerar o mapa mental.")
        st.stop()

    if app_logo_info is None: 
        logo_b64, logo_ext = get_aws_logo_base64()
        if logo_b64:
            app_logo_info = (logo_b64, logo_ext)
        else:
            app_logo_info = (None, None) 

    html_content = create_mindmap_html(df, csv_filename, app_logo_info)

    st.components.v1.html(
        html_content,
        height=900, 
        scrolling=False
    )

if __name__ == "__main__":
    main()

st.markdown("""
<style>
    .main {
        background-color: #ffffff;
        color: #333333;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    /* Esconde completamente todos os elementos da barra padrão do Streamlit */
    header {display: none !important;}
    footer {display: none !important;}
    #MainMenu {display: none !important;}
    /* Remove qualquer espaço em branco adicional */
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    /* Remove quaisquer margens extras */
    .element-container {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;">
    <h4>AWS MindMap pro: o seu mapa mental aberto e livre, 100% gratuito.</h4>
    💬 Por <strong>Ary Ribeiro</strong>. Contato, através do email: <a href="mailto:aryribeiro@gmail.com">aryribeiro@gmail.com</a><br>
    <em>Obs.: o web app foi testado apenas em computador.</em>
</div>
""", unsafe_allow_html=True)