// Small helpers shared by the reader, library and print buttons.

export function download(filename, text, type = "text/plain") {
  const blob = new Blob([text], { type: type + ";charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function safeName(s) {
  return String(s || "case").replace(/[^\w\- ]+/g, "").trim().replace(/\s+/g, "-").slice(0, 60) || "case";
}

/** Print the page with a temporary title so "Save as PDF" proposes a sensible file name. */
export function printWithTitle(title) {
  const old = document.title;
  const restore = () => {
    document.title = old;
    window.removeEventListener("afterprint", restore);
  };
  window.addEventListener("afterprint", restore);
  document.title = title;
  window.print();
}
