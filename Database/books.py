from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

import httplib2
import json

from databaseSchema import Base, Book, Author

# used to create a database
engine = create_engine('sqlite:///myLibrary.db')
# below is used to create session to query databases, comment this when
# creating database
# engine = create_engine('sqlite:///Database/myLibrary.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


def getBook(title, author, id):

    fullName = author
    user_id = id
    session.add(Author(fullName, user_id))
    session.commit()

    google_api_key = "AIzaSyA45bkUPjdBS9v8cOLS2UpP8GqGPCxfYG4"
    title = title.replace(" ", "+")
    author = author.replace(" ", "+")
    # use below url if you want to grab a book using the tile
    # and author of the book
    # url = ('https://www.googleapis.com/books/v1/volumes?q="%s"+inauthor:%s&key=AIzaSyA45bkUPjdBS9v8cOLS2UpP8GqGPCxfYG4' % (title, author))  # noqa
    #  use below url if you wnat to grab books by an author
    url = ('https://www.googleapis.com/books/v1/volumes?q=author:"%s"&key=AIzaSyA45bkUPjdBS9v8cOLS2UpP8GqGPCxfYG4' % (author))  # noqa

    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if statement check to see if the object totalItems exists
    if result['totalItems'] < 1:
        print title + author + "No book found"
    else:
        i = 0
        while i < len(result['items']):
            # finding all keys that exist in the object volumeInfo
            keyList = []
            for s in result['items'][i]['volumeInfo']:
                keyList.append(s)
            # retrieves only the keys that I want that are within volumeInfo
            keysWanted = ['title', 'authors', 'subtitle', 'description',
                          'publishedDate', 'pageCount', 'categories', 'imageLinks']  # noqa
            # compares keysWanted to that of keyList, stores list of keys that
            # match
            findMatches = set(keyList) & set(keysWanted)
            print i
            # assigns values to the keys that match
            for key in findMatches:
                if key == 'title':
                    title = result['items'][i]['volumeInfo']['title']
                elif key == 'authors':
                    author = result['items'][i]['volumeInfo']['authors'][0]
                    fullName = result['items'][i]['volumeInfo']['authors'][0]
                elif key == 'subtitle':
                    subtitle = result['items'][i]['volumeInfo']['subtitle']
                elif key == 'description':
                    description = result['items'][i][
                        'volumeInfo']['description']
                elif key == 'publishedDate':
                    published_date = result['items'][i][
                        'volumeInfo']['publishedDate']
                elif key == 'pageCount':
                    pages = result['items'][i]['volumeInfo']['pageCount']
                elif key == 'categories':
                    category = result['items'][i][
                        'volumeInfo']['categories'][0]
                elif key == 'imageLinks':
                    try:
                        image = result['items'][i]['volumeInfo'][
                            'imageLinks']['thumbnail']
                    except:
                        image = 'https://www.flickr.com/photos/26312642@N00/6630719431/'  # noqa
            # compares keysWanted to that of keyList, stores list of keys that
            # do not match
            noMatches = set(keysWanted) - set(keyList)
            # assigns values to keys that don't match
            for key in noMatches:
                if key == 'title':
                    title = "Not Listed"
                elif key == 'authors':
                    author = "Not Listed"
                elif key == 'subtitle':
                    subtitle = "Not Listed"
                elif key == 'description':
                    description = "Not Listed"
                elif key == 'publishedDate':
                    published_date = "Not Listed"
                elif key == 'pageCount':
                    pages = "Not Listed"
                elif key == 'categories':
                    category = "Not Listed"
                elif key == 'imageLinks':
                    image = ''

            webReaderLink = result['items'][i][
                'accessInfo']['accessViewStatus']
            if webReaderLink == "NONE":
                webReaderLink = result['items'][i]['volumeInfo']['infoLink']
            else:
                webReaderLink = result['items'][i][
                    'accessInfo']['webReaderLink']

            user_id = id
            idAuthor = session.query(func.max(Author.id)).one()

            session.add(Book(title, subtitle, author, idAuthor[
                        0], description, published_date, pages, webReaderLink, category, image, user_id))  # noqa
            session.commit()

            i += 1

print "added books!"
# use google books to see if the book is searchable
if __name__ == '__main__':
    getBook("The Island of Dr. Moreau", "H.G. Wells", 1)
    getBook("The Running Man", "W. A. Harbinson", 1)
    getBook("The People Shapers", "Vance Packard", 1)
    getBook("Exploring Space with a camera", "Edgar M. Cortright", 1)
    getBook("Project Blue Book", "Brad Steiger", 1)
    getBook("Intercept", "Renato Vesco", 1)
    getBook("Natural Magick", "John Baptista Porta", 1)
    getBook("Corporation Man", "Antony Jay", 1)
    getBook("Hidden Life of Freemasonry", "C. W. LeadBeater", 1)
    getBook("The Singularity Is Near: When Humans Transcend Biology",
            "Ray Kurzweil", 1)
    getBook("Sexual Symbolism: A History of Phallic Worship",
            "Richard Payne Knight", 1)
    getBook("The Perennial Philosophy", "Aldous Huxley", 1)
    getBook("the story of civilization", "Will Durant", 1)
    getBook("White Stains", "Aleister Crowley", 1)
    getBook("People from the Other World", "Henry Steel Olcott", 1)
    getBook("The one made act", "Theodore Roscoe", 1)
    getBook("The Lion and the Unicorn: Socialism and the English Genius",
            "George Orwell", 1)
    getBook("Autobiography of Mark Twain", "Mark Twain", 1)
    getBook("Zanoni", "Edward Bulwer Lytton Baron Lytton", 1)
    # getBook("Genesis", "W. A. Harbison")  # noqa
    # getBook("The First Men on the Moon", "H.G. Wells")  # noqa
    # getBook("Magic Unveiled", "Baron Du Potet")  # noqa
    # getBook("The occult establishment", "James Webb")  # noqa
    # getBook("History of German Guided Missiles", "R.F. Pocock")  # noqa
    # getBook("Man Modified: An Exploration of the Man/machine Relationship", "David Fishlock")  # noqa
    # getBook("As Man Becomes Machine", "David M. Rorvik")  # noqa
    # getBook("Antarctica", "Eliot Porter")  # noqa
    # getBook("Stryker's Kingdom", "W. A. Harbinson")  # noqa
    # getBook("Mysteries: An Investigation into the Occult, the Paranormal and the Supernatural", "Colin Wilson")  # noqa
    # getBook("Inside the Black Room: (Studies of Sensory Deprivation)", "Jack A. Vernon")  # noqa
    # getBook("Things Kept Secret From The Foundation of the World", "")  # noqa
    # getBook("Sea currents", "Julian Felix")  # noqa
    # getBook("The Instruments of Death", "W. A. Harbinson")  # noqa
    # Books down below are not cleaned.  # noqa
    # getBook("The Geography of Strabo", "Strabo")  # noqa
    # getBook("The Unconscious God", "Viktor E. Frankl")  # noqa
    # getBook("The Magic Mountain", "Thomas Mann")  # noqa
    # getBook("The book of the damned", "Charles Hoy Fort")  # noqa
    # getBook("The Spirit of Laws", "Charles-Louis De Montesquieu")  # noqa
    # getBook("The book of Ser Marco Polo", "Marco Polo")  # noqa
    # getBook("Essays on Buddhism in China and Upper Asia", "Schott")  # noqa
    # getBook("Ancient America", "Baldwin")  # noqa
    # getBook("Prehistoric Nations", "Baldwin")  # noqa
    # getBook("The Occult Sciences", "Ben David")  # noqa
    # getBook("The New Chemistry", "Josiah Cooke")  # noqa
    # getBook("The Court and Camp of Runjeet Sing", "William Godolphin Osborne")  # noqa
    # getBook("Steganographic", "Abbe Tritleim")  # noqa
    # getBook("Night-side of Nature", "C. Crowe")  # noqa
    # getBook("Thoughts on the Birth and Generation of Things", "Oetinger")  # noqa
    # getBook("Immortality of the Soul", "Dr. H. More")  # noqa
    # getBook("Unit 31", "Matt Keefe")  # noqa
    # getBook("Unit 731", "Peter Williams")  # noqa
    # getBook("The Scarlet Letter", "Nathaniel Hawthorne")  # noqa
    # getBook("Icon and Axe", "James Hadley Billington")  # noqa
    # getBook("The Devil in Connecticute", "Gerald Brittle")  # noqa
    # getBook("Apocrypha", "")  # noqa
    # getBook("People from the Other World", "Colonel H.S. Olcott")  # noqa
    # getBook("Dweller of the Threshold", "Bulwer Lytton")  # noqa
    # getBook("Supernatural religion; an inquiry into the reality of divine revelation", "Walter Richard Cassels")  # noqa
    # getBook("Iamblichus Life of Pythagoras", "Iamblichus")  # noqa
    # getBook("Moon-o-theism: Religion of a War and Moon God Prophet", "Yoel Natan")  # noqa
    # getBook("A physician's problems", "Charles M.D.")  # noqa
    # getBook("On manners and customs", "Max Muller")  # noqa
    # getBook("Porphyry: De Sacrificiis", "Porphyry")  # noqa
    # getBook("History of Magic", "Joseph Ennemoser")  # noqa
    # getBook("Zanoni", "Bulwer-Lytton")  # noqa
    # getBook("Ancient fragments", "I. P. Cory")  # noqa
    # getBook("Anacalypsis", "Godfrey Higgins")  # noqa
    # getBook("Modern forms of Magic", "Maximilian Perty")  # noqa
    # getBook("The Philosophy of Magic", "E. Salverte")  # noqa
    # getBook("Miscregenation: The Theory of the Blending of the Races Applied to the American White Man and Negro", "")  # noqa
    # getBook("Improvement of Society", "Dick")  # noqa
    # getBook("Celetial Scenery", "Dick")  # noqa
    # getBook("Decline and Fall of the roman empire", "Gibbon")  # noqa
    # getBook("Some Recollections of a Busy Life: The Forgotten Story of the Real Town of Hollister, California", "T.S. Hawkins")  # noqa
    # getBook("The new prosperity: permanent employment, wise taxation and equitable distribution of wealth", "Bernard London")  # noqa
    # getBook("Democracy in America", "Alexis de Tocqueville")  # noqa
    # getBook("the first global revolution", "Alexander King")  # noqa
    # getBook("Environmental Handbook", "Garret de Bell")  # noqa
    # getBook("Adventure in Constructive Finance", "Carter Glass")  # noqa
    # getBook("Triumphant Democracy", "Andrew Carnegie")  # noqa
    # getBook("Montagu Norman", "John Hargrave")  # noqa
    # getBook("The Web of Conspiracy", "Theodore Roscoe")  # noqa
    # getBook("The one made act", "Theodore Roscoe")  # noqa
    # getBook("The Assassins", "Robert J. Donovan")  # noqa
    # getBook("The War on Gold", "Anthony Sutton")  # noqa
    # getBook("Principles of Constitutional law", "M. Cooley")  # noqa
    # getBook("Worker's Paradise Lost", "Eugene Lyons")  # noqa
    # getBook("My Life", "Trotsky")  # noqa
    # getBook("A Wreath of Appreciation", "Andrew Jackson")  # noqa
    # getBook("Coningsby", "Benjamin Disreaeli")  # noqa
    # getBook("The Economic Consequences of the peace", "John Maynard Keynes")  # noqa
    # getBook("David Ricardo, The Works and Correspondence of David Ricardo, Vol. 4 Pamphlets and Papers 1815-1823", "David Ricardo")  # noqa
    # getBook("the intelligent woman's guide to socialism and capitalism", "George Bernard Shaw")  # noqa
    # getBook("Lords of Proverty", "Graham Hancock")  # noqa
    # getBook("Fabian Freeway: Highway to socialism in the USA", "Rose L. Martin")  # noqa
    # getBook("The Great Deceit: Social Pseudo - Sciences", "Zygmund Dobbs")  # noqa
    # getBook("Warburg the Revolutionist", "Harold Kellock" )  # noqa
    # getBook("Sutton, Wall Street and F.D.R", "Antony C. Sutton")  # noqa
    # getBook("Secrets of the Temple", "William Greider")  # noqa
    # getBook("From Farm Boy to Financier", "Frank. A. Vanderlip")  # noqa
    # getBook("Nelson W. Aldrich in American Politics", "Nathaniel Wright Stephenson")  # noqa
    # getBook("The long road home", "James Warburg")  # noqa
    # getBook("Images of America; the Jekyll island club", "Tyler E. Bagwell")  # noqa
    # getBook("The Federal Reserve Act; Its origin and Problems", "J. Laurence Laughlin")  # noqa
    # getBook("Inquiry into Human Faculty", "Francas Galton")  # noqa
    # getBook("The Two Destinies", "Wilkie Collins")  # noqa
    # getBook("Key to Theosophy", "Blavatsky")  # noqa
    # getBook("Fragments of Occult truth", "Mr. A. P. Sinnett")  # noqa
    # getBook("A strage story", "Bulwer Lytton")  # noqa
    # getBook("Three Books of Occult Philosophy", "Heinrich Cornelius Agrippa")  # noqa
    # getBook("The Magus", "Francis Barrett")  # noqa
    # getBook("The Rosicrucians", "Hargrave Jennings")  # noqa
    # getBook("Philosophy of Magic, Prodigies and Apparent Miracles", "Eusebe Salverte")  # noqa
    # getBook("The History of the Supernatural", "William Howitt")  # noqa
    # getBook("Nineteenth century Miracle", "Mrs. Hardinge Britten")  # noqa
    # getBook("Hypnotism", "Dr. A. Moll")  # noqa
    # getBook("The Royal Masonic Cyclopaedia", "Kenneth R. H. Mackenzle")  # noqa
    # getBook("Fallacies of Darwinis", "Dr. C. R. Bree")  # noqa
    # getBook("Lectures on the origin and growth of religion as illustrated by the religion of the ancient Babylonians", "Sayce, A. H.")  # noqa
    # getBook("FBI Secrets: An Agents Expose", "M. Wesley Swearingen")  # noqa
    # getBook("Orders to kill", "William P. Peppered")  # noqa
    # getBook("Ponder on this", "alice bailey")  # noqa
    # getBook('The builders', "Alice Bailey")  # noqa
    # getBook("The Lion and the Unicorn: Socialism and the English Genius", "George Orwell")  # noqa
    # getBook("Introduction to the Vendidad", "J. Darmsteter")  # noqa
    # getBook("Nabatean Agriculture", "the Orientalist Chwolson")  # noqa
    # getBook("Ruins of Empires", "Volney")  # noqa
    # getBook("Prometheus Bound", "Aeschylus")  # noqa
    # getBook("History of Paganism in Caledonia", "Dr. Th. A. Wise")  # noqa
    # getBook("The countries of the world", "Robert Brown")  # noqa
    # getBook("She: A history of Adventure", "Mr. Rider Haggard")  # noqa
    # getBook("Occult World", "Mr. Sinnett")  # noqa
    # getBook("Atlantis, the Antediluvian world", "Donnelly")  # noqa
    # getBook("Histoire de la magic", "Eliphas levi")  # noqa
    # getBook("Perfect way", "Dr. A. Kingsford")  # noqa
    # getBook("Wonders by Land and sea", "Shan Hai King")  # noqa
    # getBook("Mythical Monsters", "Charles Gould")  # noqa
    # getBook("Science of Thought", "Max Muller")  # noqa
    # getBook("Electrogravitics systems", "Thomas Valone")  # noqa
    # getBook("Posthumous Humanity", "H.S. Olcott")  # noqa
    # getBook("The Primeval Race Double-sexed", "Prof. Wilder's Essay")  # noqa
    # getBook("The Authoritarian Personality", "Theodor W. Adorno")  # noqa
    # getBook("Arte Chymiae", "Roger Bacon")  # noqa
    # getBook("Humbugs of the World", "P. T. Barnum")  # noqa
    # getBook("Faraday, as a Discoverer", "Mr. Tyndall")  # noqa
    # getBook("The Gnostics and Their Remains", "Charles King")  # noqa
    # getBook("Our Figures", "Max Mulller")  # noqa
    # getBook("Geological Evidences of the Antiquity of Man", "Sir Charles Lyell")  # noqa
    # getBook("Transactions of the Society of Biblical Archaeology", "")  # noqa
    # getBook("Assyrian Antiquities", "Mr. George Smith")  # noqa
    # getBook("The origin and significance of the great pyramid", "Mr. Stainland Wake")  # noqa
    # getBook("The source of measures", "Mr. R. Skinner")  # noqa
    # getBook("History of Civilization", "H.T. Buckle")  # noqa
    # getBook("The mysteries of Magic", "A.E. Waite")  # noqa
    # getBook("On the Origin of Life", "Blanchard")  # noqa
    # getBook("The Book of Concealed Myster", "Sephra Dezenoutha")  # noqa
    # getBook("The History of Magic", "P. christian")  # noqa
    # getBook("New Aspects of Life and Religion", "Henry Pratt M.D.")  # noqa
    # getBook("The Aphorisms of Sandilya", "Edward Byles Cowell")  # noqa
    # getBook("A Manual of Hindu Pantheism: The Vedantasara", "Major G.A. Jacob")  # noqa
    # getBook("Key to the hebrew-egyptian myster in the source of measures", "J. Ralston Skinner")  # noqa
    # getBook("Esoteric Buddhism", "Mr. Sinnett")  # noqa
    # getBook("History of the Great American Fortunes", "Mr. Sinnett")  # noqa
    # getBook("Psychology of crowds", "Gustave Le Bon")  # noqa
    # getBook("Rational Optimist", "Matthew Ridley")  # noqa
    # getBook("Why I Wave the Confederate Flag, Written by a Black Man: The End of Niggerism and the Welfare State", "Anthony Hervey")  # noqa
    # getBook("The history of Computing", "IBM")  # noqa
    # getBook("Journey into the Whirlwind", "Eugenia Ginzberg")  # noqa
    # getBook("Not a fellow traveler", "Osip Brik")  # noqa
    # getBook("The human group", "George C. Homans")  # noqa
    # getBook("The human choice: Individuation, reason and order versus de-individualization", "Phillip Zimbardo")  # noqa
    # getBook("The fund of sociability", "Robert S. Weiss")  # noqa
    # getBook("Man and Superman", "Bernard Shaw")  # noqa
    # getBook("White Stains", "Aleister Crowley")  # noqa
    # getBook("We the living", "Ayn Rand")  # noqa
    # getBook("The Strike became Atlas Shrugged", "Ayn Rand")  # noqa
    # getBook("The Fountaind Head", "Ayn Rand")  # noqa
    # getBook("The Harmless People", "Elizabeth Marshall Thomas")  # noqa
    # getBook("The Forest People", "Desmond Morrison")  # noqa
    # getBook("Squeaky: The Life and Times Of Lynette Alice Fromme", "Jess Bravin")  # noqa
    # getBook("The discovery of withces", "Hopkins")  # noqa
    # getBook("Devils, drugs and doctors", "Howard W. Haggard")  # noqa
    # getBook("An Inquiry Into the Causes and Effects of the Variolae Vaccinae, Or Cow-Pox", "")  # noqa
    # getBook("Great Herbal", "Emperor Shen Lung")  # noqa
    # getBook("Two New Sciences", "Galileo galilei")  # noqa
    # getBook("watchers of the sky", "alfred nayes")  # noqa
    # getBook("The King in Yellow", "Robert W. Chambers")  # noqa
    # getBook("Reasonableness of Christianity", "John Locke")  # noqa
    # getBook("System of Nature", "D' Holback")  # noqa
    # getBook("Book of Fallacies", "Bentham")  # noqa
    # getBook("The elements of the art of packing", "Bentham")  # noqa
    # getBook("Declaration of independence", "Carl Lotus Becker")  # noqa
    # getBook("A history of freedom of thought", "J.B. Bury")  # noqa
    # getBook("Man makes himself", "Childe V. Gordon")  # noqa
    # getBook("Greek Way to Western Civilization", "Edith Hamilton")  # noqa
    # getBook("Rules for Radicals", "Saul D. Alinsky")  # noqa
    # getBook("What Is Mathematics? An Elementary Approach to Ideas and Methods", "Herbert Robbins")  # noqa
    # getBook("after its kind", "byron nelson")  # noqa
    # getBook("New Account of East Indies and Perisa", "John Fryer")  # noqa
    # getBook("The country farm", "Gervase Markham")  # noqa
    # getBook("Discourses", "Joshua Reynolds")  # noqa
    # getBook("A Relation of Some Yeares Travaile, Begunne Anno 1626. Into Afrique and the Greater Asia", "Thomas Herbert")  # noqa
    # getBook("The Rule of Reason", "Thomas Wilson")  # noqa
    # getBook("The Painting of the Ancients", "Francis Junius")  # noqa
    # getBook("The three princes of serendip", "Horace Walpole")  # noqa
    # getBook("October Surprise", "Barbara Honegger")  # noqa
    # getBook("Battle for the Mind: A Physiology of Conversion and Brainwashing - How Evangelists, Psychiatrists, Politicians, and Medicine Men Can Change Your Beliefs and Behavior", "William Sargant")  # noqa
    # getBook("Minerva Mundi", "Hermes Trismegistus")  # noqa
    # getBook("A New Freedom", "Woodrow Wilson")  # noqa
    # getBook("De Iside et Osiride", "Plutarch")  # noqa
    # getBook("Inside the company", "Phillip Agee")  # noqa
    # getBook("Envoys of Mankind: A declaration of First principles for the governance of Space", "George S. Robinson")  # noqa
    # getBook("Cloak and scholar of the secret war", "Robert Winks")  # noqa
    # getBook("Majestic", "Whitley Striber")  # noqa
    # getBook("A strange harvest", "Linda Howe")  # noqa
    # getBook("Cosmic Conspiracy", "Stan Deyo")  # noqa
    # getBook("Crises in Democracy", "Huntington")  # noqa
    # getBook("Moongate", "William Brian")  # noqa
    # getBook("Wealth of Nations", "Adam Weishaupt")  # noqa
    # getBook("The Phoenix", "Manly P. Hall")  # noqa
    # getBook("The Richest man in babylon", "George Carson")  # noqa
    # getBook("Think and Grow Rich", "Napoleon Hill")  # noqa
    # getBook("Awake The Giant Within", "Tony Robbins")  # noqa
    # getBook("The Autobiography of Malcolm X", "Alex Haley and Malcolm X")  # noqa
    # getBook("Dark Alliance", "Gary Webb")  # noqa
    # getBook("The Sirius Mystery", "Robert K. G. Temple")  # noqa
    # getBook("Impact of Science on Society", "Bertrand Russell")  # noqa
    # getBook("Dark Alliance", "Gary Webb")  # noqa
    # getBook("The Sirius Mystery", "Robert K. G. Temple")  # noqa
    # getBook("The Impact of Science on Society", "Bertrand Russell")  # noqa
    # getBook("Magnetic Current", "Edward Leedskalnin")  # noqa
    # getBook("The Myth of the Twentieth Century", "Alfred Rosenberg")  # noqa
    # getBook("The Arcane Schools", "John Yarker")  # noqa
    # getBook("Rise of the Warrior Cop: The Militarization of America's Police Forces", "Radley Balko")  # noqa
    # getBook("Moonchild", "Aleister Crowley")  # noqa
    # getBook("The unheavenly city revisited", "Edward C. Banfield")  # noqa
    # getBook("You Owe Yourself a Drunk: An Ethnography of Urban Nomads", "James Spradley")  # noqa
    # getBook("Of Spies and Stratagems: Incredible Secrets of World War II Revealed By a Master Spy", "Stanley Lovell")  # noqa
    # getBook("The Future of the Human Mind: A Study of the Potential Powers of the Brain", "George H. Estabrooks")  # noqa
    # getBook("The CIA and the Cult of Intelligence", "Victor Marchetti")  # noqa
    # getBook("The control candy jones", "donald bain")  # noqa
    # getBook("Operation Mind Control", "Walter Bowart")  # noqa
    # getBook("What is to be done", "V. I. Lenin")  # noqa
    # getBook("Stranger in a Strange Land", "Robert Heinlein")  # noqa
    # getBook("The hidden persuaders", "Vance Packard")  # noqa
    # getBook("Darkness at noon", "Arthur Koestler")  # noqa
    # getBook("A history of penal methods", "George Ives")  # noqa
    # getBook("The Mind Possessed: A Physiology of Possession, Mysticism, and Faith Healing", "William Sargant")  # noqa
    # getBook("The Road to Serfdom", "Frederick A Hayek")  # noqa
    # getBook("Bending the Twig", "Augustin C. Rudd")  # noqa
    # getBook("Social Problems and Scientism", "A. H. Hobbs")  # noqa
    # getBook("Collectivism on the campus: The battle for the mind in American colleges", "E. Merrill Root")  # noqa
    # getBook("The Tipping Point How little things can make a big difference", "Malcom Gladwell")  # noqa
    # getBook("Cult and Ritual abuse", "James Noblitt")  # noqa
    # getBook("Silent Night", "Staley Weintraub")  # noqa
    # getBook("The hero with a thousand faces", "Joseph Campbell")  # noqa
    # getBook("The Informant: A True Story", "Kurt Eichenwald")  # noqa
    # getBook("Weapons of fraud: a source book for fraud fighters", "doug shaded")  # noqa
    # getBook("On Killing", "Dave Grossman")  # noqa
    # getBook("Photographing the Holocaust", "Janina Struk")  # noqa
    # getBook("Ordinary Men: Reserve Police Battalion 101 and the Final Solution in Poland", "Christopher Browning")  # noqa
    # getBook("Without Sanctuary: Lynching Photography in America", "James Allen")  # noqa
    # getBook("Better for all the world: the secret history of forced sterilization and America's quest for racial purity", "Harry Bruinius")  # noqa
    # getBook("Violence workers", "Martha Knisely Huggins")  # noqa
    # getBook("The Family", "Sanders")  # noqa
    # getBook("Helter Skelter", "Ed Sanders")  # noqa
    # getBook("The Mind Manipulators", "Alan W. Scheflin")  # noqa
    # getBook("Marine Machine", "William Mares")  # noqa
    # getBook("Pygmalion in the Classroom", "Robert Rosenthal")  # noqa
    # getBook("The Human Zoo: A Zoologist's Class Study of The Urban Animal", "Desmond Morris")  # noqa
    # getBook("Quiet Heroes: True Stories of the Rescue of Jews by Christians in Nazi-occupied Holland", "Andre Stein")  # noqa
    # getBook("Escape from Freedom", "Erich Fromm")  # noqa
    # getBook("The image, or, What happened to the American dream", "Daniel J. Boorstin")  # noqa
    # getBook("The Nazi doctors", "Robert Jay Lifton")  # noqa
    # getBook("An invitation to Social Psychology: Expressing and censoring the self", "Dale Miller")  # noqa
    # getBook("The Most Dangerous Book in the World: 9/11 as Mass Ritual", "S. K. Bain")  # noqa
    # getBook("Your money's worth", "F. J. Schlink")  # noqa
    # getBook("Hypnotism and Suggestion", "Louis Satow")  # noqa
    # getBook("Treason in America", "Anton Chaitkin")  # noqa
    # getBook("Ricardo's law", "Fred Harrison")  # noqa
    # getBook("Return of the Magi Paperback", "Maurice Magre")  # noqa
    # getBook("Beasts Men and Gods", "Ferdinand Ossendowski")  # noqa
    # getBook("The house that Hitler built", "Stephen Henry Roberts")  # noqa
    # getBook("will europe follow atlantis", "spense")  # noqa
    # getBook("Nazification of Art: Art, Design, Architecture Music and Film in Third Reich", "Brandon Taylor")  # noqa
    # getBook("They Wanted War", "otto D. tolischus")  # noqa
    # getBook("The Occult Establishment", "James Webb")  # noqa
    # getBook("Atlantis in Andalucia: A study of folk memory", "Ellen M Whishaw")  # noqa
    # getBook("Occult Causes of the Present War", "Lewis Spence")  # noqa
    # getBook("The English Spy", "Bernard BlackMantle")  # noqa
    # getBook("Philosophy in the Bedroom", "Marquis de Sade")  # noqa
    # getBook("120 Days of Sodom", "Donatien Alphonse Francois De Sade")  # noqa
    # getBook("Patriots: The Men Who Started the American Revolution", "A. J. Langguth")  # noqa
    # getBook("The English Physician's Guide or a Holy Guide", "John Heydon")  # noqa
    # getBook("The Republic of Plato", "James Adam")  # noqa
    # getBook("Autobiography of Mark Twain", "Mark Twain")  # noqa
    # getBook("Gods Heroes and Men of Ancient Greece", "W. H. D. Rouse")  # noqa
    # getBook("Origin of Russian Communism", "N. Derdyaer")  # noqa
    # getBook("Georgian Adventure : The Autobiography of Douglas Jerrold", "Douglas Jerrold")  # noqa
    # getBook("On the Beach", "Nevil Shute")  # noqa
    # getBook("USSR: The Corrupt Society: The Secret World of Soviet Capitalism", "Konstantin M. Simis")  # noqa
    # getBook("A Letter to American Workers", "Vladmir Lenin")  # noqa
    # getBook("Left-Wing Communism: An Infantile Disorder", "Vladimir Lenin")  # noqa
    # getBook("Anti-Duhring", "Friedrich Engels")  # noqa
    # getBook("Critique of the Gotha Program", "Karl Marx")  # noqa
    # getBook("Das Kapital", "Engels")  # noqa
    # getBook("the illiteracy of the literate", "H. R. Huse")  # noqa
    # getBook("People in Quandaries", "Alfred Korzgbski")  # noqa
    # getBook("The Open Conspiracy", "H. G. Wells")  # noqa
    # getBook("looking backward", "Edward Bellamy")  # noqa
    # getBook("The satanists", "Peter Haning")  # noqa
    # getBook("Business fraud know it and prevent it", "James A. Blanco")  # noqa
    # getBook("Confessions of a Barbaria", "George Sylvester Viereck")  # noqa
    # getBook("book of lies", "Crowley")  # noqa
    # getBook("Russia in the Shadows", "H. G. Wells")  # noqa
    # getBook("Bacteriophage: Genetics and Molecular Biology", "")  # noqa
    # getBook("Great Computer: A Vision", "Olof Johannesson")  # noqa
    # getBook("Profiles of the Future", "Arthur C. Clarke")  # noqa
    # getBook("Walden Two", "B. F. Skinner")  # noqa
    # getBook("the stars of peace and war", "Louis De Wohl")  # noqa
    # getBook("Back to Methuselah", "Bernard Shaw")  # noqa
    # getBook("The Case Against Tomorrow", "Frederik Pohl")  # noqa
    # getBook("Daedalus; or, Science and the future", "John Burdon Sanderson Haldane")  # noqa
    # getBook("Book 777", "Crowley")  # noqa
    # getBook("Language in Thought and Action", "S. I. Hayakawa")  # noqa
    # getBook("looking backward", "Edward Bellamy")  # noqa
    # getBook("Propaganda & the American Revolution 1763-1783", "Philip Davidson")  # noqa
    # getBook("The Man Who Would Be King", "")  # noqa
    # getBook("The Equinox of the Gods: The Official Organ of the A.-.A.-.", "Alesiter Crowley")  # noqa
    # getBook("Physical Control of the Mind: Toward a Psychocivilized Society", "Jose Manuel Rodriguez Delgado")  # noqa
    # getBook("propaganda", "Edward Bernays")  # noqa
    # getBook("Thus Spoke Zarathustra", "friedrich Nietzsche")  # noqa
    # getBook("What's Killing You and What to Do About It!", "Daivd Hamilton")  # noqa
    # getBook("Allergie", "Clemens Peter Pirquet Von Cesenatico")  # noqa
    # getBook("The Grand Inquisitor", "Fyodor Dostoyevsky")  # noqa
    # getBook("I'll Take My Stand: The South and the Agrarian Tradition", "Louis D. Jr. Rubin")  # noqa
    # getBook("Space toward the year 2018", "Gordon J. F. Macdonald")  # noqa
    # getBook("The Technological Society", "Jacques Ellul")  # noqa
    # getBook("The Global City", "Jacques Ellul")  # noqa
    # getBook("Creating a New Civilization: The Politics of the Third Wave", "Theodore H. Von Laue")  # noqa
    # getBook("Creating a New Civilization: The Politics of the Third Wave", "Alvin Toffler")  # noqa
    # getBook("Born in Blood: The Lost Secrets of Freemasonry", "John J. Robinson")  # noqa
    # getBook("LEVEl 7", "Mordecai Roshwald")  # noqa
    # getBook("The Fable of the Bees", "Bernard Mandeville")  # noqa
    # getBook("An Economic Interpretation of the Constitution of the United States", "Charles Austin Beard")  # noqa
    # getBook("The Founding of the Second British Empire 1763 - 1793", "Vincent T. Harlow")  # noqa
    # getBook("The History Of The Seal Of The United States", "Gillard Hunt")  # noqa
    # getBook("born in blood: the lost secrets of fremasonry", "John J. Robinson")  # noqa
    # getBook("The Clergy and the Craft", "Forrest D. Haggard")  # noqa
    # getBook("Secret Societies and Subversive Moments", "Nesta Webster")  # noqa
    # getBook("Occult Theocrasy", "Edith Starr Miller")  # noqa
    # getBook("Mystic Masonry", "Dr. J. D. Buck")  # noqa
    # getBook("Textbook of Masonic Jurisprudence", "Albert Mackey")  # noqa
    # getBook("Morals and Dogma", "Albert Pike")  # noqa
    # getBook("father of lies", "Warren Weston")  # noqa
    # getBook("the story of civilization", "Will Durant")  # noqa
    # getBook("Proof of a conspiracy against all the religions and governments of europe", "John Robinson")  # noqa
    # getBook("Halley's Bible Handbook", "Henry Hampton Halley")  # noqa
    # getBook("Face the music", "Leonard J. Seidel")  # noqa
    # getBook("The Heartbeat of the Dragon: The Occult Roots of Rock and Roll", "Mark Spaulding")  # noqa
    # getBook("Behind the Lodge Door: Church, State and Freemasonry in America", "Paul A. Fisher")  # noqa
    # getBook("a world with jews", "Karl Marx")  # noqa
    # getBook("The jewish nigger", "Karl Marx")  # noqa
    # getBook("Philip Dru: Administrator", "Edward M. House")  # noqa
    # getBook("KKK: Ku Klux Klan: It's origin, Growth and Disbandment", "J. C. Lester")  # noqa
    # getBook("The Ultimate evil", "Maury Terry")  # noqa
    # getBook("The Brotherhood: The Secret World of the Freemasons", "Stephen Thomas Knight")  # noqa
    # getBook("To eliminate the opiate", "Marvin S Antelman")  # noqa
    # getBook("The Naked Capitalist", "W. Cleon Skousen")  # noqa
    # getBook("Origins of the Balfour Declaration: Dr. Weizmann's Contribution", "James A. Malcolm")  # noqa
    # getBook("Who Financed Hitler", "James Poole")  # noqa
    # getBook("The Master Spy", "Phillip Knighley")  # noqa
    # getBook("Jack the Ripper", "Stephen Knight")  # noqa
    # getBook("Fire in the minds of men: origins of the revolutionary faith", "James Hadley Billington")  # noqa
    # getBook("The New Dark Ages Conspiracy", "Carol White")  # noqa
    # getBook("Thunder at Twilight", "Frederic Morton")  # noqa
    # getBook("Rienzi: the last roman tribunes", "Lytton")  # noqa
    # getBook("The Unknown Hitler", "Wolf Schwarzwaller")  # noqa
    # getBook("Who financed hitler", "James Pool")  # noqa
    # getBook("Adolf Hitler and the Age to come", "Kurt Von Ensen")  # noqa
    # getBook("Trading with the enemy", "Charles Higham")  # noqa
    # getBook("the international jew", "Ford")  # noqa
    # getBook("The ideal initiate", "Oswald Wirth")  #noqa
