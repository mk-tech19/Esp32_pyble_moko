HTML = r"""<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STM32 Flasher</title>
<style>
body{font:16px system-ui;max-width:720px;margin:2rem auto;padding:0 1rem;background:#f5f7fb;color:#182235}
main{background:white;border:1px solid #d8deea;border-radius:14px;padding:1.2rem}
button{padding:.8rem 1rem;border:0;border-radius:8px;background:#174a8b;color:white;font-weight:700}
input{display:block;margin:1rem 0;max-width:100%}pre{white-space:pre-wrap;background:#eef2f7;padding:1rem;border-radius:8px}
.warning{color:#8a3000;background:#fff0df;padding:.8rem;border-radius:8px}
</style></head><body><main>
<h1>ESP32 → STM32 Flasher</h1>
<p class="warning"><b>Prototipe belum tervalidasi.</b> Pastikan BOOT0 HIGH dan target adalah board uji.
Erase/write hanya tersedia jika safety lock pada config.py sengaja diaktifkan.</p>
<label>Firmware .bin <input id="file" type="file" accept=".bin,application/octet-stream"></label>
<p id="meta">Pilih berkas firmware.</p>
<label><input id="confirm" type="checkbox"> Saya memahami target dapat terhapus dan perlu recovery.</label>
<p><button id="flash">Mulai flashing</button></p>
<pre id="status">Siap.</pre>
<script>
const f=document.querySelector('#file'), meta=document.querySelector('#meta');
const status=document.querySelector('#status'), btn=document.querySelector('#flash');
f.onchange=()=>{const x=f.files[0];meta.textContent=x?`${x.name} — ${x.size} byte`:'Pilih berkas firmware.'};
btn.onclick=async()=>{
 const x=f.files[0];
 if(!x){status.textContent='Pilih file .bin terlebih dahulu.';return}
 if(!document.querySelector('#confirm').checked){status.textContent='Centang konfirmasi risiko dahulu.';return}
 if(!x.name.toLowerCase().endsWith('.bin')){status.textContent='Hanya file .bin yang diterima.';return}
 btn.disabled=true;status.textContent='Mengirim file...';
 try{
  const r=await fetch('/flash',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(x.name)},body:x});
  status.textContent=(r.ok?'HASIL: ':'GAGAL: ')+await r.text();
 }catch(e){status.textContent='Koneksi terputus: '+e}
 finally{btn.disabled=false}
};
</script></main></body></html>"""
