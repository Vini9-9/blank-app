import json
import os
import streamlit as st
from typing import List, Dict, Optional
from st_clipboard import copy_to_clipboard

# Configuração da página
st.set_page_config(
    page_title="Catálogo de Produtos",
    page_icon="🛒",
    layout="wide"
)

# Estilo CSS customizado
st.markdown("""
<style>
    .product-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .product-price {
        color: #2e7d32;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .product-source {
        color: #666;
        font-size: 0.85rem;
        margin-top: 8px;
    }
    .category-header {
        background: linear-gradient(90deg, #1976d2, #42a5f5);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .product-image {
        border-radius: 8px;
        object-fit: cover;
        width: 100%;
        max-height: 200px;
    }
</style>
""", unsafe_allow_html=True)

def carregar_produtos(arquivo: str = "produtos_bff.json") -> Optional[List[Dict]]:
    """
    Carrega os produtos do arquivo JSON
    
    Args:
        arquivo: Nome do arquivo JSON
    
    Returns:
        Lista de produtos ou None se erro
    """
    try:
        if not os.path.exists(arquivo):
            st.error(f"❌ Arquivo '{arquivo}' não encontrado!")
            return None
        
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        if not dados:
            st.warning("⚠️ O arquivo JSON está vazio!")
            return None
        
        # Se for um dicionário com chave 'produtos'
        if isinstance(dados, dict) and 'produtos' in dados:
            produtos = dados['produtos']
        # Se for diretamente uma lista
        elif isinstance(dados, list):
            produtos = dados
        else:
            st.error("❌ Formato do JSON inválido! Esperado lista ou objeto com chave 'produtos'")
            return None
        
        return produtos
    
    except json.JSONDecodeError:
        st.error("❌ Erro ao ler o JSON: arquivo mal formatado!")
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        return None

def organizar_por_categoria(produtos: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Organiza os produtos por categoria
    
    Args:
        produtos: Lista de produtos
    
    Returns:
        Dicionário com categorias e seus produtos
    """
    categorias = {}
    
    for produto in produtos:
        categoria = produto.get('categoria', 'Sem categoria')
        if categoria not in categorias:
            categorias[categoria] = []
        categorias[categoria].append(produto)
    
    return categorias

def montar_texto_compartilhamento(produto: Dict) -> str:
    """
    Monta o texto para compartilhamento da oferta
    
    Args:
        produto: Dicionário com dados do produto
    
    Returns:
        Texto formatado para compartilhamento
    """
    nome = produto.get('nome', 'Produto')
    preco = produto.get('menor_preco', 0)
    fonte = produto.get('fonte', '')
    link = produto.get('link', '')
    cupom = produto.get('cupom', None)
    descricao = produto.get('descricao', '')
    
    texto = f"🛍️ {nome}\n"
    
    if descricao:
        texto += f"\n{descricao}\n"
    
    if preco:
        preco_formatado = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        texto += f"\n💰 Preço: {preco_formatado}"
    
    if fonte:
        texto += f"\n🏪 Loja: {fonte}"
    
    if cupom:
        texto += f"\n🎫 Com esse cupom fica ainda mais barato: {cupom}"
    
    if link:
        texto += f"\n🔗 {link}"
    
    return texto

def exibir_produto(produto: Dict):
    """
    Exibe um único produto no formato de card
    
    Args:
        produto: Dicionário com dados do produto
    """
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Imagem do produto
            imagem_url = produto.get('imagem', '')
            if imagem_url:
                st.image(imagem_url, use_container_width=True)
            else:
                st.markdown("""
                <div style="background:#f5f5f5; height:200px; display:flex; align-items:center; justify-content:center; border-radius:8px;">
                    <span style="color:#999;">Sem imagem</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Nome do produto
            st.markdown(f"### {produto.get('nome', 'Produto sem nome')}")
            
            # Menor preço encontrado
            preco = produto.get('menor_preco', 0)
            if preco:
                preco_formatado = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.markdown(
                    f'''
                    <div class="product-price">
                        <div style="font-size: 12px; color: #777;">A partir de:</div>
                        <div style="font-size: 18px; font-weight: bold;">💰 {preco_formatado}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
            else:
                st.markdown('<div class="product-price">💰 Preço não informado</div>', unsafe_allow_html=True)
            
            # Descrição (se tiver)
            # if produto.get('descricao'):
            #     st.caption(produto.get('descricao'))

            if produto.get('ranking'):
                st.caption('Melhor posição na categoria: ' + produto.get('ranking'))
            
            # Fonte e Link
            fonte = produto.get('fonte', 'Fonte não informada')
            link = produto.get('link', '#')
            cupom = produto.get('cupom', None)  # Pega o cupom se existir
            if cupom:
                
                # Container estilizado para o cupom
                with st.container():
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 8px;
                        padding: 12px;
                        text-align: center;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        <span style="
                            color: white;
                            font-size: 1.5rem;
                            font-weight: bold;
                            letter-spacing: 3px;
                            font-family: monospace;
                        ">Cupom de desconto</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(cupom, language="txt")
                
                
                st.markdown('</div>', unsafe_allow_html=True)
                    
            # Botão/link para oferta
            if link and link != '#':
                st.markdown(f'<div class="product-source">🏪 {fonte}</div>', unsafe_allow_html=True)
                # Se tiver cupom, adiciona texto explicativo
                texto_botao = "🔗 Ver oferta →"
                if cupom:
                    texto_botao = "👀 Link exclusivo para o cupom →"
                
                st.markdown(f'<a href="{link}" target="_blank"><button style="background:#1976d2; color:white; padding:8px 16px; border:none; border-radius:5px; cursor:pointer; margin-top:10px; width:100%;">{texto_botao}</button></a>', unsafe_allow_html=True)
                
                # Montar texto de compartilhamento
                texto_share = montar_texto_compartilhamento(produto)
                share_id = f"share_{hash(produto.get('nome', ''))}"
                
                if st.button("📋 Copiar oferta", key=share_id, use_container_width=True):
                    copy_to_clipboard(texto_share)
                    st.success("✅ Oferta copiada para área de transferência!")
            else:
                st.markdown('<div class="product-source">🔗 Link indisponível</div>', unsafe_allow_html=True)
        
        st.divider()

def main():
    """
    Função principal da aplicação
    """
    # Título principal
    st.title("🛍️ Catálogo de Produtos")
    st.markdown("---")
    
    # Carregar produtos
    produtos = carregar_produtos()
    
    if not produtos:
        st.info("💡 Dica: Certifique-se de que o arquivo 'produtos_bff.json' existe e está no formato correto.")
        
        # Exemplo de estrutura esperada
        with st.expander("📖 Ver exemplo de estrutura do JSON"):
            st.code("""
{
  "produtos": [
    {
      "nome": "Produto Exemplo",
      "categoria": "Eletrônicos",
      "imagem": "https://exemplo.com/imagem.jpg",
      "menor_preco": 99.90,
      "fonte": "Loja Exemplo",
      "link": "https://exemplo.com/produto",
      "descricao": "Descrição opcional do produto"
    }
  ]
}
            """, language="json")
        return
    
    # Organizar por categoria
    categorias = organizar_por_categoria(produtos)
    
    # Exibir produtos por categoria
    for categoria, lista_produtos in categorias.items():
        # Cabeçalho da categoria
        st.markdown(f'<div class="category-header"><h2> {categoria}</h2><p>{len(lista_produtos)} produto(s)</p></div>', unsafe_allow_html=True)
        
        # Exibir produtos em grid (2 colunas)
        cols = st.columns(2)
        for idx, produto in enumerate(lista_produtos):
            with cols[idx % 2]:
                exibir_produto(produto)
        
        st.markdown("---")

if __name__ == "__main__":
    main()