function getBrowserHeight() {
    return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
}

let height = getBrowserHeight()

const tiles = document.getElementsByTagName("article")[0].children
const colors = [[255, 255, 255], [0, 0, 0], [255, 43, 6], [0, 231, 112], [255, 139, 252], [247, 144, 30]]
const topShadow = document.getElementById("top-shadow")
const bottomShadow = document.getElementById("bottom-shadow")

const gradient = (degree, gradient) => {
    return `linear-gradient(${degree}deg, transparent,rgb(${gradient}))`
}


const updateShadows = () => {
    let doBottom = true
    let doTop = true
    for (let i=0; i<tiles.length; i++) {
        if (tiles[i].offsetTop + height > window.scrollY && doTop) {
            topShadow.style.background = gradient(0, colors[i])
            doTop = false
        }
        if ((tiles[i].offsetTop + height/2) > window.scrollY && doBottom) {
            bottomShadow.style.background = gradient(180, colors[i+1])
            doBottom = false
        }
        }
}

updateShadows()

window.addEventListener("scroll", () => {
    if (window.scrollY < height) {
        updateShadows()
    }
}) 

window.addEventListener("resize", () => {
    height = getBrowserHeight()
})