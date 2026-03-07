function create() {
const version = document.getElementById("version").value;

if (version) {
    const createPopup = document.getElementById("creating");
    const bg = document.getElementById("video");

    createPopup.style.opacity = "100%";
    bg.style.filter = "brightness(40%)";

    document.getElementById("createForm").remove();

    fetch(`/launcher/api/create/${version}`).catch(err => console.error(err));

    location.href = "/launcher/base";
} else {
    alert("Please select a version");
}

}
