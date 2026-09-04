const { Authflow } = require("prismarine-auth");
const fs = require("fs");

async function login() {
    const authflow = new Authflow(
        "xbox-launcher-user",
        "./auth-cache"
    );

    const xboxToken = await authflow.getXboxToken();

    const response = await fetch(
        `https://profile.xboxlive.com/users/xuid(${xboxToken.userXUID})/profile/settings?settings=Gamertag`,
        {
            headers: {
                "Authorization": `XBL3.0 x=${xboxToken.userHash};${xboxToken.XSTSToken}`,
                "x-xbl-contract-version": "2"
            }
        }
    );

    const data = await response.json();

    const username = data.profileUsers[0].settings.find(
        setting => setting.id === "Gamertag"
    ).value;

    fs.writeFileSync("username.txt", username);
}

login();
