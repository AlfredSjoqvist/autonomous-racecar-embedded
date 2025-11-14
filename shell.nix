{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
      python-lsp-ruff
      python-lsp-server
      tkinter
      websockets
    ]))
  ];
}
