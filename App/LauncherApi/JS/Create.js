function create() {
                    const version = document.getElementById("version").value;
                    if (version) {
                        const createPopup = document.getElementById("creating");
                        const bg = document.getElementById("video");
                        createPopup.style.opacity = "100%";
                        bg.style.filter = "brightness(40%)";
                        document.getElementById("createForm").remove();
                        async function waitForOK(url) {
                            try {
                                const res = await fetch(url, { timeout: 0 });
                                const text = (await res.text()).trim();

                                if (text === "OK") {
                                    location.href = "/launcher/library";
                                } else {
                                    alert("Error: " + text);
                                    location.href = "/launcher/library";
                                }
                            } catch (err) {
                                alert("Request failed: " + err);
                            }
                        }


                        waitForOK(`/launcher/api/create/${version}`);


                    } else {
                        alert("Please select a version");
                    }
                }
