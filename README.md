# Windows Jarvis (Local GPT-OSS Agent)

Bu depo, Windows 10/11 üzerinde yerel LLM (vLLM, CUDA) + OS/Web otomasyon + RAG + saydam HUD (Electron) ile çalışan bir Jarvis aracını içerir.

## Hızlı Başlangıç (Tek Komut Kurulum)

PowerShell (Administrator) açın:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
cd jarvis
./install.ps1 -Model "openai/gpt-oss-20b" -UseYarn:$true
```

Kurulum sonrası başlatmak için:

```powershell
./startup/start_agent.ps1 -Model "openai/gpt-oss-20b"
```

> Not: Daha büyük model (örn. GPT-120B) için `-Model` parametresini değiştirip `--tensor-parallel-size` gibi vLLM bayraklarını `configs/config.toml` içinden ayarlayabilirsiniz. VRAM gereksinimi yüksektir.

## Gereksinimler
- Windows 10/11 (x64)
- NVIDIA Driver + CUDA 12.1+ + cuDNN
- Python 3.11 (x64), Git, Node.js 20+ (Yarn opsiyonel)

Kurulum betiği eksik olanları `winget` ile yüklemeyi dener.

## Yapı

- `core/`: Orkestratör, durum makinesi, LLM istemci, RAG, ses
- `tools/`: OS, tarayıcı, FS, OCR vb. araçlar
- `overlay-ui/`: Electron tabanlı saydam HUD
- `configs/`: Konfigürasyon ve kişisel veri filtreleri
- `startup/`: Başlatma ve zamanlayıcı betikleri
- `data/`, `logs/`: Çalışma verileri

## Çalıştırma
1. vLLM API ayağa kalkar (OpenAI uyumlu `/v1/chat/completions`).
2. Python ajan WebSocket sunucusu (HUD ile konuşur) ve araç kayıtlarını başlatır.
3. HUD üzerinden açılış onayı gelir; onay sonrası arka planda çalışır.

## Notlar
- Tesseract OCR için `winget install -e --id UB-Mannheim.TesseractOCR` önerilir.
- `configs/personal_filters.toml` ile PII filtreleme aktif edilir.
- Görev zamanlayıcı kaydı için `startup/schedule.xml` ve ilgili komutlar mevcuttur.
