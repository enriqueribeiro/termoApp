import os
import uuid
import time
from flask import Flask, render_template, request, send_file, after_this_request, jsonify
try:
    from .utils import DocumentEditor, SheetsHandler
except ImportError:
    from utils import DocumentEditor, SheetsHandler
from dotenv import load_dotenv
from datetime import datetime
try:
    from .logger import logger, log_request_start, log_request_end, log_google_sheets_operation, log_file_operation
    from .exceptions import (
        TermoAppException, DocumentGenerationError, GoogleSheetsError, 
        FileOperationError, ValidationError, ConfigurationError, 
        TemplateNotFoundError
    )
    from .cache import GoogleSheetsCache
    from .validation import FormValidator
except ImportError:
    from logger import logger, log_request_start, log_request_end, log_google_sheets_operation, log_file_operation
    from exceptions import (
        TermoAppException, DocumentGenerationError, GoogleSheetsError, 
        FileOperationError, ValidationError, ConfigurationError, 
        TemplateNotFoundError
    )
    from cache import GoogleSheetsCache
    from validation import FormValidator

# Load environment variables
load_dotenv()

# Configuration validation
SHEET_ID = os.getenv("SHEET_ID")
CREDENTIALJSON = os.getenv("CREDENTIALS")

# Don't raise exceptions at import time - validate when needed

app = Flask(__name__)

# Setup logging
logger.info("TermoApp starting up")

# Mapeamento de departamentos
DEPARTAMENTOS_WEB = {
    "ti": "TI",
    "rh": "People & Culture",
    "administrativo": "ADM/Financeiro",
    "marketing": "Marketing",
    "comercial": "Comercial",
    "desenvolvimento": "Desenvolvimento",
    "central": "Central de REL.",
    "juridico": "Juridico"
}

# Ensure output folders exist
os.makedirs('entrega_docx', exist_ok=True)
os.makedirs('entrega_pdf', exist_ok=True)

@app.route('/', methods=["GET", "POST"])
def index():
    """
    Main page: handles form submission and document generation.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log request start
    log_request_start(
        request_id=request_id,
        method=request.method,
        endpoint=request.endpoint or '/',
        ip_address=request.remote_addr or 'unknown',
        user_agent=request.headers.get('User-Agent', 'Unknown')
    )
    
    if request.method == "POST":
        try:
            # Validate configuration
            if not SHEET_ID:
                raise ConfigurationError("SHEET_ID environment variable is required", "SHEET_ID")
            if not CREDENTIALJSON:
                raise ConfigurationError("CREDENTIALS environment variable is required", "CREDENTIALS")
            
            # 1. Collect and validate form data from user
            dados_usuario = {
                "nome": (request.form.get("nome") or "").upper(),
                "funcao": (request.form.get("funcao") or "").upper(),
                "departamento": (DEPARTAMENTOS_WEB.get(str(request.form.get("departamento"))) or "").upper(),
                "numero": request.form.get("telefone") or "",
                "empresa": (request.form.get("empresa") or "").lower()
            }
            
            # Use the new validation system
            form_validator = FormValidator()
            is_valid, validation_errors = form_validator.validate_form_data(request.form)
            
            if not is_valid:
                # Return detailed validation errors
                return jsonify({
                    "error": "Validation failed",
                    "validation_errors": validation_errors
                }), 400
            
            # Handle 'other' role
            if dados_usuario["funcao"] == "OUTROS":
                dados_usuario["funcao"] = request.form.get("outrosFuncao", "").upper()
            
            patrimonios = request.form.getlist('patrimonio[]')
            observacoes = request.form.getlist('observacao[]')
            
            logger.info("Form data validated successfully")
            # 2. Criar documento com ba eno template
            modelo = f"entrega{dados_usuario['empresa']}.docx"  # Modelo padrão
            modelo_path = os.path.join("modelos", modelo)
            
            if not os.path.exists(modelo_path):
                raise TemplateNotFoundError(
                    f"Template não encontrado: {modelo}",
                    template_name=modelo,
                    available_templates=[f for f in os.listdir("modelos") if f.endswith('.docx')]
                )
            
            try:
                editor = DocumentEditor(documento_entrada=modelo_path)
                log_file_operation("load", modelo_path, True)
            except Exception as e:
                log_file_operation("load", modelo_path, False, str(e))
                raise DocumentGenerationError(f"Erro ao carregar template: {e}", modelo_path, dados_usuario)
            
            # Format phone number
            numero_formatado = editor.formata_numero(dados=dados_usuario)
            dados_usuario["numero"] = numero_formatado if numero_formatado is not None else ""
            
            # Replace basic data in document
            editor.substituir_texto({
                "nome": dados_usuario["nome"],
                "funcao": dados_usuario["funcao"],
                "numero": dados_usuario["numero"],
                "empresa": dados_usuario["empresa"]
            })
            # 3. Process each asset with caching and safety limits
            if not SHEET_ID:
                raise GoogleSheetsError("SHEET_ID not configured", "", "metadata_fetch")
            
            # Safety limit: maximum 10 assets per request to prevent mass updates
            MAX_ASSETS_PER_REQUEST = 10
            if len(patrimonios) > MAX_ASSETS_PER_REQUEST:
                raise ValidationError(
                    f"Máximo de {MAX_ASSETS_PER_REQUEST} patrimônios por requisição permitido",
                    "patrimonio"
                )
            
            sh = SheetsHandler(SHEET_ID)
            try:
                # Try to get sheet metadata from cache first
                sheet_names = GoogleSheetsCache.get_sheet_metadata(SHEET_ID)
                log_google_sheets_operation("metadata_fetch", "cached", True)
            except Exception as e:
                logger.warning(f"Cache miss for sheet metadata: {e}")
                sheet_names = sh.obter_metadados()
                if not sheet_names:
                    log_google_sheets_operation("metadata_fetch", "all", False, "Failed to connect to Google Sheets")
                    raise GoogleSheetsError("Erro ao conectar com a planilha", SHEET_ID, "metadata_fetch")
                log_google_sheets_operation("metadata_fetch", "all", True)
            
            # Store all found items
            todos_itens = []
            assets_not_found = []
            total_updates = 0
            MAX_UPDATES_PER_REQUEST = 50  # Safety limit for total spreadsheet updates
            
            for i, patrimonio in enumerate(patrimonios):
                if patrimonio:
                    try:
                        # Try to get search results from cache
                        resultados = GoogleSheetsCache.search_assets(SHEET_ID, patrimonio, sheet_names)
                        log_google_sheets_operation("asset_search", patrimonio, True)
                    except Exception:
                        logger.warning(f"Cache miss for asset search: {patrimonio}")
                        sh = SheetsHandler(SHEET_ID)
                        resultados = sh.buscar_palavra_em_abas(patrimonio, sheet_names)
                        log_google_sheets_operation("asset_search", patrimonio, bool(resultados))
                    
                    if resultados:
                        # Safety check: limit number of results per asset to prevent mass updates
                        if len(resultados) > 5:
                            logger.warning(f"Too many results for {patrimonio}: {len(resultados)} results, limiting to 5")
                            resultados = resultados[:5]
                        
                        # For each result (item) found for this asset
                        for resultado in resultados:
                            # Safety check: limit total updates
                            if total_updates >= MAX_UPDATES_PER_REQUEST:
                                logger.warning(f"Reached maximum updates limit ({MAX_UPDATES_PER_REQUEST}) for request")
                                break
                            
                            aba, linha, valores = resultado
                            try:
                                # Update spreadsheet
                                sh = SheetsHandler(SHEET_ID)
                                sh.altera_proprietario(SHEET_ID, aba, linha, dados_usuario["nome"])
                                sh.altera_departamento(SHEET_ID, aba, linha, dados_usuario["departamento"])
                                total_updates += 1
                                log_google_sheets_operation("update_owner", f"{aba}:{linha}", True)
                            except Exception as e:
                                log_google_sheets_operation("update_owner", f"{aba}:{linha}", False, str(e))
                                logger.warning(f"Failed to update spreadsheet for {patrimonio}: {e}")
                            
                            # Add to document
                            lista_filtrada = sh.filtrar_lista_por_aba(aba, valores)
                            if len(lista_filtrada) >= 2:
                                dados_tabela = [
                                    "01",
                                    " ".join(lista_filtrada[:-1]),
                                    lista_filtrada[-1]
                                ]
                                todos_itens.append({
                                    "dados": dados_tabela,
                                    "observacao": observacoes[i] if i < len(observacoes) and observacoes[i] else "",
                                    "patrimonio": patrimonio
                                })
                    else:
                        assets_not_found.append(patrimonio)
                        logger.warning(f"Asset not found: {patrimonio}")
            
            if assets_not_found:
                logger.warning(f"Assets not found: {assets_not_found}")
                # Continue processing but log the missing assets
            # 4. Add items to document
            patrimonio_atual = None
            for item in todos_itens:
                # Add row with item data
                editor.adicionar_linha_tabela(item["dados"])
                # If asset changed, add note
                if item["patrimonio"] != patrimonio_atual:
                    if item["observacao"]:
                        editor.adicionar_linha_mesclada(f"OBS: {item['observacao'].upper()}")
                    patrimonio_atual = item["patrimonio"]
            # 5. Clean up old files before creating new ones
            try:
                # Delete old files from previous requests
                for folder in ['entrega_docx', 'entrega_pdf']:
                    if os.path.exists(folder):
                        for old_file in os.listdir(folder):
                            if old_file.startswith(f"Termo_entrega_{dados_usuario['nome']}_"):
                                old_path = os.path.join(folder, old_file)
                                try:
                                    os.remove(old_path)
                                    logger.info(f"Deleted old file: {old_path}")
                                except Exception as e:
                                    logger.warning(f"Could not delete old file {old_path}: {e}")
            except Exception as e:
                logger.warning(f"Error during cleanup of old files: {e}")
            
            # 6. Generate unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_base = f"Termo_entrega_{dados_usuario['nome']}_{timestamp}"
            docx_path = os.path.join('entrega_docx', f"{nome_base}.docx")
            base_dir = os.path.dirname(app.root_path)
            pdf_path = os.path.join(base_dir, 'entrega_pdf', f"{nome_base}.pdf")
            # 7. Save DOCX
            editor.documento.save(docx_path)
            # 8. Convert to PDF
            editor.converter_para_pdf_libreoffice(
                nomedoc=docx_path, 
                pasta_saida='entrega_pdf'
            )
            if not os.path.exists(pdf_path):
                return f"Erro: PDF não gerado em {pdf_path}", 500
            # 9. Return PDF for download with cleanup after download completes
            @after_this_request
            def cleanup(response):
                # Add a small delay to ensure download starts
                time.sleep(0.5)
                for path in [docx_path, pdf_path]:
                    try:
                        if os.path.exists(path):
                            # Try multiple times with delays
                            for attempt in range(3):
                                try:
                                    os.remove(path)
                                    break
                                except PermissionError:
                                    if attempt < 2:  # Not the last attempt
                                        time.sleep(1)  # Wait 1 second before retry
                                    else:
                                        app.logger.warning(f"Could not delete {path} after 3 attempts")
                                except Exception as e:
                                    app.logger.error(f"Erro ao excluir {path}: {str(e)}")
                                    break
                    except Exception as e:
                        app.logger.error(f"Erro ao excluir {path}: {str(e)}")
                return response
            
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f"Entrega {dados_usuario['nome']}.pdf",
                mimetype='application/pdf'
            )
        except ValidationError as e:
            logger.warning(f"Validation error: {e.message}")
            return jsonify({"error": e.message, "field": e.field}), 400
        except GoogleSheetsError as e:
            logger.error(f"Google Sheets error: {e.message}")
            return jsonify({"error": f"Erro na planilha: {e.message}"}), 500
        except DocumentGenerationError as e:
            logger.error(f"Document generation error: {e.message}")
            return jsonify({"error": f"Erro na geração do documento: {e.message}"}), 500
        except TemplateNotFoundError as e:
            logger.error(f"Template not found: {e.message}")
            return jsonify({"error": f"Template não encontrado: {e.message}"}), 404
        except FileOperationError as e:
            logger.error(f"File operation error: {e.message}")
            return jsonify({"error": f"Erro de arquivo: {e.message}"}), 500
        except TermoAppException as e:
            logger.error(f"Application error: {e.message}")
            return jsonify({"error": e.message}), 500
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500
        finally:
            # Log request end
            response_time = time.time() - start_time
            log_request_end(request_id=request_id, response_time=response_time, status_code=200)
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)