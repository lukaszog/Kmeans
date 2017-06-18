import gi

gi.require_version("GObject", "2.0")
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import csv
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from numpy import arange, sin, pi


class KMeans(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title("k srednich")
        self.connect('destroy', Gtk.main_quit)
        self.main_view = Gtk.HBox()
        self.plot_view = Gtk.VBox()
        self.box = Gtk.VBox(homogeneous=False, spacing=0)
        self.filew = ""
        button1 = Gtk.Button("Wybierz plik")
        button1.connect("clicked", self.on_file_clicked)
        self.box.add(button1)

        reset_button = Gtk.Button("Resetuj")
        reset_button.connect("clicked", self.reset)
        self.box.add(reset_button)

        self.cluster_label = Gtk.Label("Liczba skupien:")
        self.box.add(self.cluster_label)

        adjustment = Gtk.Adjustment(1, 1, 20, 1, 1, 0)
        self.h_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        self.h_scale.set_digits(0)
        self.h_scale.set_hexpand(True)
        self.h_scale.set_valign(Gtk.Align.START)
        self.h_scale.connect("value-changed", self.scale_moved)
        self.box.add(self.h_scale)

        metric_label = Gtk.Label("Wybierz rodzaj metryki:")

        name_store = Gtk.ListStore(int, str)
        name_store.append([1, "Euklidesowa"])
        name_store.append([2, "Miejska"])
        name_combo = Gtk.ComboBox.new_with_model_and_entry(name_store)
        name_combo.connect("changed", self.on_name_combo_changed)
        name_combo.set_entry_text_column(1)

        self.box.add(metric_label)
        self.box.add(name_combo)
        self.centroid_button = Gtk.Button("Wybierz centroidy")
        self.centroid_button.set_sensitive(False)
        self.centroid_button.connect("clicked", self.run_kmeans)

        self.group_button = Gtk.Button("Grupuj")
        self.group_button.set_sensitive(False)
        self.group_button.connect("clicked", self.group)


        self.scale_plot = Gtk.Button("Skaluj")
        self.scale_plot.set_sensitive(False)
        self.scale_plot.connect("clicked", self.scaled)


        self.box.add(self.centroid_button)
        self.box.add(self.group_button)
        self.box.add(self.scale_plot)
        self.data = ""
        self.cluster_count = ""
        self.metric_id = ""
        self.filename = ""
        self.plot_area = ""
        self.cluster = ""
        self.color_random = ""
        self.figure = ""
        self.cluster_centers = []
        self.plot_canvas = ""
        self.main_data_canvas = ""

        self.main_view.add(self.box)
        self.main_view.add(self.plot_view)
        self.add(self.main_view)
        self.couting = 0
        self.is_random_center = 0

        self.show_all()

    def scaled(self, event):
        plt.scatter(*zip(*self.data), c=self.color_random[self.cluster])
        plt.scatter(*zip(*self.cluster_centers), s=500, c=self.color_random, marker='v')
        plt.show()

    def run_kmeans(self, event):
        self.kmeans(self.cluster_count, self.data)

    def group(self, event):
        self.couting += 1

        if self.couting % 2 == 0:
            print "Parzysta"
            self.kmeans(self.cluster_count, self.data)
            # self.plot_area.scatter(*zip(*self.data))
            self.plot_area.clear()
            self.plot_area.scatter(*zip(*self.data))
            self.plot_area.scatter(*zip(*self.cluster_centers), s=500, c=self.color_random, marker='v')
            self.plot_canvas.draw()
            self.plot_view.show_all()

        else:
            print "Nieparzysta"

            self.plot_area.scatter(*zip(*self.data), c=self.color_random[self.cluster])
            self.plot_area.scatter(*zip(*self.cluster_centers), s=500, c=self.color_random, marker='v')
            self.plot_canvas.draw()
            self.plot_view.show_all()


    def on_name_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            self.metric_id = row_id
            # 1 euklidesowa
            # 2 miejsca
            print("Selected: ID=%d, name=%s" % (row_id, name))
        else:
            entry = combo.get_child()
            print("Entered: %s" % entry.get_text())

    def scale_moved(self, event):
        self.cluster_count = self.h_scale.get_value()

    def on_file_clicked(self, widget):
        print "clikc"
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            self.filename = dialog.get_filename()
            dialog.destroy()
            self.openfile(self.filename)

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

    def openfile(self, filename):

        with open(filename) as csvfile:
            self.data = [(float(x), float(y)) for x, y in csv.reader(csvfile, delimiter=",")]

        self.load_data_from_file()

    def load_data_from_file(self):
        self.centroid_button.set_sensitive(True)
        self.group_button.set_sensitive(True)
        self.scale_plot.set_sensitive(True)

        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        a.scatter(*zip(*self.data))
        self.main_data_canvas = FigureCanvas(f)
        self.plot_view.add(self.main_data_canvas)
        self.plot_view.show_all()
        self.resize(1000,400)

    def euclides_distance(self, p1, p2):
        dist = 0.0
        for i in xrange(0, len(p2)):
            dist += (p1[i] - p2[i]) ** 2
        return math.sqrt(dist)

    def manhattan_distance(self, x, y):

        return sum(abs(a - b) for a, b in zip(x, y))

    def kmeans(self, k, data):
        self.color_random = np.arange(k)

        # wymiar danych
        dim = len(data[0])

        # lista zer
        cluster = [0] * len(data)
        # lista -1
        prev_cluster = [-1] * len(data)

        i = 0
        max_iter = 1000

        if self.is_random_center == 0:
            for i in xrange(0, int(k)):
                self.cluster_centers += [random.choice(data)]

            self.is_random_center = 1

        # while (cluster != prev_cluster) or i > max_iter:
        prev_cluster = list(cluster)
        i += 1
        print "Iteracja numer"
        # print "Cluster {}".format(cluster)

        for x in xrange(0, len(data)):
            min_dist = float("inf")

            # sprawdzenie minimalnego dystansu miedzy srodkami
            for y in xrange(0, len(self.cluster_centers)):
                distance = ""
                if self.metric_id == 2:
                    distance = self.manhattan_distance(data[x], self.cluster_centers[y])
                else:
                    distance = self.euclides_distance(data[x], self.cluster_centers[y])

                if distance < min_dist:
                    min_dist = distance
                    cluster[x] = y

        # aktualizacja srodkow
        for k in xrange(0, len(self.cluster_centers)):
            new_center = dim * [0]
            members = 0
            for p in xrange(0, len(data)):
                if cluster[p] == k:  # ten punkt nalezy do klastra
                    for j in xrange(0, dim):
                        new_center[j] += data[p][j]
                        # print "Nowy srodek {}".format(new_center[j])
                    members += 1

            for j in xrange(0, dim):
                if members != 0:
                    new_center[j] = new_center[j] / float(members)

            self.cluster_centers[k] = new_center

        print self.cluster_centers

        self.cluster = cluster

        if self.couting == 0:
            print "Rysuje"
            self.figure = Figure(figsize=(5, 4), dpi=100)
            self.plot_area = self.figure.add_subplot(111)
            self.plot_area.scatter(*zip(*data))
            self.plot_area.scatter(*zip(*self.cluster_centers), s=500, c=self.color_random, marker='v')
            self.plot_canvas = FigureCanvas(self.figure)
            self.plot_canvas.draw()
            self.plot_canvas.show_all()
            self.plot_view.add(self.plot_canvas)
            self.plot_view.show()
            self.plot_view.show_all()

    def reset(self, event):
        self.plot_view.remove(self.plot_canvas)
        self.plot_view = Gtk.VBox()
        self.plot_view.show_all()
        self.couting = 0
        self.is_random_center = 0


if __name__ == "__main__":
    k = 3
    # kmeans(k=k, data=data)

    win = KMeans()
    win.show_all()
    Gtk.main()
