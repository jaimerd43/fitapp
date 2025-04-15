const input = document.getElementById("foto");
const preview = document.getElementById("preview");
const cargando = document.getElementById("cargando");
const resultado = document.getElementById("resultado");

input.addEventListener("change", () => {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    preview.src = e.target.result;
    preview.classList.remove("hidden");
  };
  reader.readAsDataURL(file);
});

async function enviarFoto() {
  const archivo = input.files[0];
  if (!archivo) return alert("Primero selecciona o toma una foto");

  cargando.classList.remove("hidden");
  resultado.textContent = "";

  const formData = new FormData();
  formData.append("foto", archivo);

  try {
    const res = await fetch("/procesar-foto", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    resultado.textContent = data.resultado;
  } catch (err) {
    resultado.textContent = "Ocurrió un error al procesar la imagen.";
  } finally {
    cargando.classList.add("hidden");
  }
}
