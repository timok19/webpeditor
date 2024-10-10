document.addEventListener("DOMContentLoaded", function () {
  const navLinks = document.querySelectorAll(".nav-link");

  const currentUrl = window.location.href;

  navLinks.forEach((link) => {
    if (link.href === currentUrl) {
      link.className = "nav-link block py-2 pl-3 pr-4 text-white bg-blue-700 rounded md:bg-transparent " +
        "md:text-blue-700 md:p-0 md:dark:text-blue-500";
      link.setAttribute("aria-current", "page");
    } else {
      link.className = "nav-link block py-2 pl-3 pr-4 text-gray-900 rounded hover:bg-gray-100 " +
        "md:hover:bg-transparent md:hover:text-blue-700 md:p-0 md:dark:hover:text-blue-500 " +
        "dark:text-white dark:hover:bg-gray-700 dark:hover:text-white " +
        "md:dark:hover:bg-transparent dark:border-gray-700";
      link.removeAttribute("aria-current");
    }
  });
});
