const { app, BrowserWindow, globalShortcut } = require('electron');
const path = require('path');
const WebSocket = require('ws');

let win;
let ws;

function createWindow() {
  win = new BrowserWindow({
    width: 420,
    height: 160,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  win.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(getHtml('idle')));
}

function getHtml(state) {
  const color = ({ idle:'rgba(128,128,128,0.6)', listening:'rgba(0,128,255,0.6)', executing:'rgba(128,0,255,0.6)', confirming:'rgba(255,128,0,0.6)' })[state] || 'rgba(128,128,128,0.6)';
  return `<!doctype html><html><body style="margin:0;background:${color};color:#fff;font:14px/1.4 system-ui;padding:12px;">
  <div id="log">HUD</div>
  <div style="margin-top:8px;">
    <button onclick="send({type:'confirm_boot',accept:true})">Evet</button>
    <button onclick="send({type:'confirm_boot',accept:false})">Hayır</button>
    <button onclick="send({type:'hotkey',action:'kill'})">Kill</button>
  </div>
  <script>
  let ws;
  function log(x){ document.getElementById('log').innerText = x }
  function send(obj){ try{ ws && ws.send(JSON.stringify(obj)); }catch(e){} }
  function connect(){
    ws = new WebSocket('ws://127.0.0.1:8765');
    ws.onopen = ()=> log('Bağlandı');
    ws.onmessage = (ev)=>{
      const data = JSON.parse(ev.data);
      if(data.type==='state'){
        document.body.style.background = ({ idle:'rgba(128,128,128,0.6)', listening:'rgba(0,128,255,0.6)', executing:'rgba(128,0,255,0.6)', confirming:'rgba(255,128,0,0.6)'}[data.value] || 'rgba(128,128,128,0.6)');
        log('Durum: '+data.value)
      } else if(data.type==='boot'){
        log(data.message)
      } else if(data.type==='plan'){
        log('Plan: '+(data.steps||[]).join(' -> '))
      } else if(data.type==='result'){
        log('Sonuç: '+(data.summary||''))
      } else if(data.type==='stt'){
        log('STT: '+data.text)
      }
    }
    ws.onclose = ()=> setTimeout(connect, 1000)
  }
  connect();
  </script>
  </body></html>`
}

app.whenReady().then(()=>{
  createWindow();
  globalShortcut.register('CommandOrControl+Alt+Shift+J', ()=>{
    try{ ws && ws.send(JSON.stringify({type:'hotkey',action:'kill'})); }catch(e){}
  })
})

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit() })
