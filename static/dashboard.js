const PACK_ID = "pack_demo_5docs";
const token = localStorage.getItem("token");

if (!token) {
  window.location.href = "/login.html";
}

document.getElementById("generateBtn").onclick = () => {

  const data = {
    razon_social: document.getElementById("razon_social").value.trim(),
    r_f_c: document.getElementById("r_f_c").value.trim(),
    numero_de_contrato: document.getElementById("numero_de_contrato").value.trim(),
    nombre_completo_de_la_persona_que_firma_la_solicitud:
      document.getElementById("nombre_completo_de_la_persona_que_firma_la_solicitud").value.trim(),
    domicilio_del_cliente:
      document.getElementById("domicilio_del_cliente").value.trim(),
    monto_de_la_operacion_Sin_IVA:
      document.getElementById("monto_de_la_operacion_Sin_IVA").value.trim()
  };

  for (const k in data) {
    if (!data[k]) {
      alert("Completá todos los campos");
      return;
    }
  }

  const status = document.getElementById("statusMsg");
  const btn = document.getElementById("generateBtn");

  btn.disabled = true;
  status.textContent = "Generando documentación...";

  fetch("/client/generate-pack", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + token
    },
    body: JSON.stringify({
      pack_id: PACK_ID,
      data: data
    })
  })
  .then(r => r.json())
  .then(res => {
    btn.disabled = false;

    if (!res.ok) {
      status.textContent = "Error generando documentación";
      status.className = "status error";
      return;
    }

    status.innerHTML = `
      ✔ Documentación generada correctamente –
      <a href="${res.zip_download}" target="_blank">Descargar ZIP</a>
    `;
    status.className = "status ok";

    loadHistory();
  })
  .catch(() => {
    btn.disabled = false;
    status.textContent = "Error inesperado";
    status.className = "status error";
  });
};

function loadHistory() {
  fetch("/client/packs", {
    headers: { Authorization: "Bearer " + token }
  })
  .then(r => r.json())
  .then(res => {
    const table = document.getElementById("historyTable");
    table.innerHTML = "";

    res.packs.forEach(p => {
      table.innerHTML += `
        <tr>
          <td>${p.pack_id}</td>
          <td>${p.created_at}</td>
          <td>${p.email_sent ? "Enviado" : "Error"}</td>
          <td>
            <a href="/download/${p.zip_name}" target="_blank">ZIP</a>
          </td>
        </tr>`;
    });
  });
}

loadHistory();
