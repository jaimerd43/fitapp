async function enviarFoto() {
    const input = document.getElementById("foto");
    const archivo = input.files[0];
    if (!archivo) return alert("Primero selecciona o toma una foto");
  
    document.getElementById("cargando").style.display = "block";
    const formData = new FormData();
    formData.append("foto", archivo);
  
    const res = await fetch("/procesar-foto", {
      method: "POST",
      body: formData
    });
  
    const data = await res.json();
    document.getElementById("cargando").style.display = "none";
    document.getElementById("resultado").textContent = data.resultado;
  }
  