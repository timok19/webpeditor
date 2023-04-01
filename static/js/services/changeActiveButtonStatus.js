function updateAriaCurrentOnClick() {
  const allLinksInNavBar = document.getElementById("navbar-sticky");
  let links = [];
  //Home link
  for (let i = 0; i < allLinksInNavBar.firstElementChild.children.length; i++) {
    links.push(allLinksInNavBar.firstElementChild.children[i].firstElementChild)
  }
  console.log(links)
}

updateAriaCurrentOnClick();

