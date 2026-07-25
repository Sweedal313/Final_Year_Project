// ================= POPUP ALERT =================
function showPopup(msg){
    let p = document.createElement("div");
    p.className="popup";
    p.innerText=msg;
    document.body.appendChild(p);
    p.style.display="block";
    setTimeout(()=>p.remove(),3000);
}

window.onload=function(){
    let alerts=document.getElementsByClassName("alert-icon");
    for(let i=0;i<alerts.length;i++){
        if(alerts[i].innerText.trim()!==""){
            showPopup("⚠ Expense limit exceeded!");
            break;
        }
    }
}

// ================= PASSWORD TOGGLE =================
function togglePassword() {
    var x = document.getElementById("password");
    var icon = document.getElementById("eyeIcon");

    if (x.type === "password") {
        x.type = "text";
        icon.innerHTML = "🙈";
    } else {
        x.type = "password";
        icon.innerHTML = "👁";
    }
}