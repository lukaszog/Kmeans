import gi

gi.require_version("GObject", "2.0")
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import random
import math
import matplotlib.pyplot as plt
import csv
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from numpy import arange, sin, pi


class KMeans(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title("KMeans")
        self.connect('destroy', Gtk.main_quit)
        self.box = Gtk.VBox()
        self.filew = ""
        button1 = Gtk.Button("Wybierz plik")
        button1.connect("clicked", self.on_file_clicked)
        self.box.add(button1)

        self.cluster_label = Gtk.Label("Liczba skupien")
        self.box.add(self.cluster_label)

        adjustment = Gtk.Adjustment(1, 1, 20, 1, 1, 0)
        self.h_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        self.h_scale.set_digits(0)
        self.h_scale.set_hexpand(True)
        self.h_scale.set_valign(Gtk.Align.START)
        self.h_scale.connect("value-changed", self.scale_moved)
        self.box.add(self.h_scale)

        name_store = Gtk.ListStore(int, str)
        name_store.append([1, "Euklidesowa"])
        name_store.append([2, "Miejska"])
        name_combo = Gtk.ComboBox.new_with_model_and_entry(name_store)
        name_combo.connect("changed", self.on_name_combo_changed)
        name_combo.set_entry_text_column(1)

        self.box.add(name_combo)

        self.data = ""
        self.cluster_count = ""
        self.metric_id = ""
        self.filename = ""
        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        a.plot(t, s)
        canvas = FigureCanvas(f)
        self.box.add(canvas)
        self.add(self.box)

        self.show_all()

    def on_name_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            self.metric_id = row_id
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

        self.box.add(plt.scatter(*zip(*self.data)))

    def euclides_distance(self, p1, p2):
        dist = 0.0
        for i in xrange(0, len(p2)):
            dist += (p1[i] - p2[i]) ** 2
        return math.sqrt(dist)

    def kmeans(self, k="k", data="data"):
        colors = ['r', 'g', 'b']

        # wymiar danych
        dim = len(data[0])

        # lista zer
        cluster = [0] * len(data)
        # lista -1
        prev_cluster = [-1] * len(data)

        i = 0
        max_iter = 1000
        cluster_centers = []
        for i in xrange(0, k):
            cluster_centers += [random.choice(data)]

        while (cluster != prev_cluster) or i > max_iter:
            prev_cluster = list(cluster)
            i += 1

            for x in xrange(0, len(data)):
                min_dist = float("inf")

                # sprawdzenie minimalnego dystansu miedzy srodkami
                for y in xrange(0, len(cluster_centers)):

                    distance = self.euclides_distance(data[x], cluster_centers[y])
                    if distance < min_dist:
                        min_dist = distance
                        cluster[x] = y

                        # print "Dystans miedzy x1 {} y1 {} x2 {} y2 {} wynosi {}  ".format(data[x][0], data[x][1], data[y][0], data[y][1], distance)
                        # polaczenie punktow
                        # plt.plot(*zip(data[x], cluster_centers[y]), linestyle='--')

            # aktualizacja srodkow
            for k in xrange(0, len(cluster_centers)):
                new_center = dim * [0]
                members = 0
                for p in xrange(0, len(data)):
                    if cluster[p] == k:  # ten punkt nalezy do klastra
                        for j in xrange(0, dim):
                            new_center[j] += data[p][j]
                            print "Nowy srodek {}".format(new_center[j])
                        members += 1

                for j in xrange(0, dim):
                    if members != 0:
                        new_center[j] = new_center[j] / float(members)

                cluster_centers[k] = new_center

        print "======== Results ========"
        print "Clusters", cluster_centers
        print "Iterations", i
        print "Assignments", cluster

        plt.scatter(*zip(*data))
        plt.scatter(*zip(*cluster_centers), s=1000, c=colors, marker='v')
        plt.show()


if __name__ == "__main__":
    k = 3
    # kmeans(k=k, data=data)

    win = KMeans()
    win.show_all()
    Gtk.main()
