import reflex as rx

config = rx.Config(
    app_name="Gestao_RH_Impacta",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ]
)