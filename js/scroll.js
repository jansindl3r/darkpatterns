const download = document.getElementById("download")

window.addEventListener("scroll", () => {
    window.onscroll = function(ev) {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight && !localStorage['visited']) {
            download.click()
            localStorage['visited'] = true
        }
    }
}) 