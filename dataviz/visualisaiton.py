import pandas as pd
import plotly.graph_objects as go

class Vizu:
    def __init__(self, data_path, viz_type, name=None, color="rgba(30, 100, 200, 0.3)"):
        self.data_path = data_path
        self.viz_type = viz_type
        self.name = name or data_path
        self.color = color
        self.df = pd.read_csv(data_path, sep="\t")
        self.df.reset_index(drop=True, inplace=True)
        self.df["Index"] = self.df.index

        # Prétraitement
        self.df["Distance"] = self.df["Distance"].astype(float)
        self.df["Distance_Cumulative"] = self.df["Distance"].cumsum()

    def get_trace(self):
        if self.viz_type == "stacked":
            return go.Scatter(
                x=self.df["Index"],
                y=self.df["Distance_Cumulative"],
                fill="tozeroy",
                mode="lines",
                name=self.name,
                line=dict(color=self.color, width=3)
            )
        else:
            raise NotImplementedError("Seul le type 'stacked' est supporté ici.")

    def show(self):
        fig = go.Figure()
        fig.add_trace(self.get_trace())
        fig.update_layout(
            title=f"Erreur cumulée : {self.name}",
            xaxis_title="Entrées",
            yaxis_title="Erreur cumulée"
        )
        fig.show()


# Créer deux visualisations, chacune avec sa couleur et son nom
visualisation_3 = Vizu("../evaluations/low_granularity_with_incomplete_entry/01_vt_matches.csv", "stacked", name="Version 02", color="rgba(10, 0, 250, 0.3)")
visualisation_1 = Vizu("../evaluations/low_granularity_with_incomplete_entry/03_corpusense_raw_matches.csv", "stacked", name="Version 03", color="rgba(30, 100, 200, 0.3)")
visualisation_2 = Vizu("../evaluations/low_granularity_with_incomplete_entry/02_corpusense_boxes_matches.csv", "stacked", name="Version 02", color="rgba(200, 50, 50, 0.3)")

# Construire une figure combinée
fig = go.Figure()
fig.add_trace(visualisation_1.get_trace())
fig.add_trace(visualisation_2.get_trace())
fig.add_trace(visualisation_3.get_trace())

fig.update_layout(
    title="Comparaison des erreurs cumulées",
    xaxis_title="Entrées",
    yaxis_title="Erreur cumulée"
)

fig.show()
