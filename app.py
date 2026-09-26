import json
import os

import flet as ft

ARQUIVO = "contatos.json"



def carregar_contatos() -> list[dict]:
    """READ (arquivo): carrega a lista de contatos do JSON, se existir."""
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def salvar_contatos(contatos: list[dict]) -> None:
    """Grava a lista completa de contatos no arquivo JSON."""
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(contatos, f, ensure_ascii=False, indent=2)


def proximo_id(contatos: list[dict]) -> int:
    """Gera um id incremental unico para novos contatos."""
    if not contatos:
        return 1
    return max(c["id"] for c in contatos) + 1



def main(page: ft.Page):
    page.title = "Agenda de Contatos - CRUD com Flet"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 24
    page.window.width = 760
    page.window.height = 820

    contatos: list[dict] = carregar_contatos()
    id_em_edicao: int | None = None  # None = criando; numero = editando

   
    campo_nome = ft.TextField(label="Nome", width=320, autofocus=True)
    campo_email = ft.TextField(label="E-mail", width=320)
    campo_telefone = ft.TextField(label="Telefone", width=320)
    campo_busca = ft.TextField(
        label="Pesquisar por nome...",
        width=320,
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: atualizar_tabela(),
    )

    botao_salvar = ft.FilledButton(
        "Adicionar",
        icon=ft.Icons.ADD,
        on_click=lambda e: salvar(e)
)

    botao_cancelar = ft.OutlinedButton(
        "Limpar",
        icon=ft.Icons.CLOSE,
        on_click=lambda e: limpar_formulario()
)
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("E-mail")),
            ft.DataColumn(ft.Text("Telefone")),
            ft.DataColumn(ft.Text("Ações")),
        ],
        rows=[],
        border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
        border_radius=8,
        heading_row_color=ft.Colors.BLUE_50,
    )

    total_texto = ft.Text("", size=13, color=ft.Colors.BLUE_GREY_400)

    def avisar(mensagem: str, cor=ft.Colors.GREEN_600):
        snackbar = ft.SnackBar(
            ft.Text(mensagem),
            bgcolor=cor
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    def limpar_formulario():
        nonlocal id_em_edicao
        id_em_edicao = None
        campo_nome.value = ""
        campo_email.value = ""
        campo_telefone.value = ""
        campo_nome.error_text = None
        botao_salvar.text = "Adicionar"
        botao_salvar.icon = ft.Icons.ADD
        page.update()


    def atualizar_tabela():
        termo = (campo_busca.value or "").strip().lower()
        visiveis = [
            c for c in contatos
            if termo in c["nome"].lower() or termo in c["email"].lower()
        ]
        tabela.rows = []
        for contato in visiveis:
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(contato["id"]))),
                        ft.DataCell(ft.Text(contato["nome"])),
                        ft.DataCell(ft.Text(contato["email"])),
                        ft.DataCell(ft.Text(contato["telefone"])),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        icon_color=ft.Colors.BLUE_600,
                                        tooltip="Editar",
                                        on_click=lambda e, c=contato: iniciar_edicao(c),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        icon_color=ft.Colors.RED_600,
                                        tooltip="Excluir",
                                        on_click=lambda e, c=contato: confirmar_exclusao(c),
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )
        total_texto.value = f"{len(visiveis)} contato(s) exibido(s) de {len(contatos)} cadastrado(s)."
        page.update()


    def salvar(e):
        nonlocal id_em_edicao
        nome = (campo_nome.value or "").strip()
        email = (campo_email.value or "").strip()
        telefone = (campo_telefone.value or "").strip()

        if not nome:
            campo_nome.error_text = "O nome é obrigatório."
            page.update()
            return
        campo_nome.error_text = None

        if id_em_edicao is None:
            # CREATE
            contatos.append(
                {
                    "id": proximo_id(contatos),
                    "nome": nome,
                    "email": email,
                    "telefone": telefone,
                }
            )
            avisar(f"Contato '{nome}' adicionado com sucesso!")
        else:
            # UPDATE
            for contato in contatos:
                if contato["id"] == id_em_edicao:
                    contato["nome"] = nome
                    contato["email"] = email
                    contato["telefone"] = telefone
                    break
            avisar(f"Contato '{nome}' atualizado com sucesso!", ft.Colors.BLUE_600)

        salvar_contatos(contatos)
        limpar_formulario()
        atualizar_tabela()

    def iniciar_edicao(contato: dict):
        nonlocal id_em_edicao
        id_em_edicao = contato["id"]
        campo_nome.value = contato["nome"]
        campo_email.value = contato["email"]
        campo_telefone.value = contato["telefone"]
        botao_salvar.text = "Salvar alterações"
        botao_salvar.icon = ft.Icons.SAVE
        page.update()

   
    def confirmar_exclusao(contato: dict):
        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar exclusão"),
            content=ft.Text(
                f"Deseja realmente excluir '{contato['nome']}'?"
            ),
        )

        def fechar_dialogo(e):
            dialogo.open = False
            page.update()

        def excluir(e):
            contatos.remove(contato)
            salvar_contatos(contatos)

            dialogo.open = False
            page.update()

            avisar(
                f"Contato '{contato['nome']}' excluído.",
                ft.Colors.RED_600
            )

            atualizar_tabela()

        dialogo.actions = [
            ft.TextButton(
                "Cancelar",
                on_click=fechar_dialogo,
            ),
            ft.FilledButton(
                "Excluir",
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.RED_600
                ),
                on_click=excluir,
            ),
        ]

        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

   
    page.add(
        ft.Text("Agenda de Contatos", size=28, weight=ft.FontWeight.BOLD),
        ft.Text(
            "CRUD com Flet e persistência em arquivo JSON",
            size=14,
            color=ft.Colors.BLUE_GREY_400,
        ),
        ft.Divider(),
        ft.Row([campo_nome, campo_email], wrap=True),
        ft.Row([campo_telefone, botao_salvar, botao_cancelar], wrap=True),
        ft.Divider(),
        campo_busca,
        tabela,
        total_texto,
    )

    atualizar_tabela()


if __name__ == "__main__":
    ft.run(main)