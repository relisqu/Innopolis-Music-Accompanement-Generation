
import random
import mido
import music21
from mido import Message, MidiFile, MidiTrack,MetaMessage

FILE_NAME='input1.mid'

mid = mido.MidiFile(FILE_NAME, clip=True)
mid.type=1

#Constants
MINOR_CHORD=[0,3,7]
MAJOR_CHORD=[0,4,7]
DIM_CHORD=[0,3,6]
ALL_CHORDS = [MINOR_CHORD, MAJOR_CHORD, DIM_CHORD]
CHORD_DURATION= mid.ticks_per_beat*2


#Detect the tonic of the song
score = music21.converter.parse(FILE_NAME)
key = score.analyze('key')
if(key.mode=="minor"):
    MUSIC_SCALE=(key.tonic.midi+3)%12
else:
    MUSIC_SCALE=key.tonic.midi%12

def get_average_velocity():
    note_count=0
    avg_velocity=0
    for note in mid.tracks[1]:
        if isinstance(note, Message) and ( note.type == 'note_on'):
            avg_velocity+=note.velocity
            note_count+=1
    return int(avg_velocity/note_count)


def get_average_octave():
    note_count=0
    avg_octave=0
    for note in mid.tracks[1]:
        if isinstance(note, Message) and ( note.type == 'note_on'):
            avg_octave+=int(note.note/12)
            note_count+=1
    return int(avg_octave/note_count)


class Chord:
    def __init__(self, root_note, chord_type):
        """Constructor"""
        self.root_note= root_note
        self.type= chord_type
        self.note_list= [(root_note + note) % 12 for note in chord_type]
        pass
    def has_note(self, note):
        if(note==None):
             return False
        for chord_note in self.note_list:
            if(chord_note == note % 12):
                return True
        return False
    def __eq__(self, other): 
        return self.root_note == other.root_note and self.type == other.type

class Accompanement:
    def __init__(self, scale, size):
        self.scale= scale
        self.size=size
        self.consonantChords = []
        self.consonantChords.append(Chord(scale % 12,        MAJOR_CHORD))
        self.consonantChords.append(Chord((scale + 5) % 12,  MAJOR_CHORD))
        self.consonantChords.append(Chord((scale + 7) % 12,  MAJOR_CHORD))
        self.consonantChords.append(Chord((scale + 9) % 12,  MINOR_CHORD))
        self.consonantChords.append(Chord((scale + 2) % 12,  MINOR_CHORD))
        self.consonantChords.append(Chord((scale + 4) % 12,  MINOR_CHORD))
        self.consonantChords.append(Chord((scale + 11) % 12, DIM_CHORD))
        pass
    def get_consonant_chord(self,note):
        for chord in self.consonantChords:
            if(chord.has_note(note)):
                return chord
        return random.choice(self.consonantChords)

    def print_all_notes(self):
        note_list = []
        for chord in self.consonantChords:
            for note in chord.note_list:
                if note not in note_list:
                    note_list.append(note)

    def has_in_consonant_chords(self, chord):
        for existing_chord in self.consonantChords:
            if(existing_chord==chord):
                return True
        return False
    def has_note_in_consonant_chords(self, note):
        if(note==None):
            return False 
        for existing_chord in self.consonantChords:
            if(existing_chord.has_note(note%12)):
                return True
        return False
        
    
CIRCLE_OF_FIFTHS = [[0,  7, 2,  9, 4, 11, 6, 1,  8, 3, 10, 5], # TRIAD_MAJOR 
                    [9,  4, 11, 6, 1, 8,  3, 10, 5, 0, 7,  2], # TRIAD_MINOR
                    [11, 6, 1,  8, 3, 10, 5, 0,  7, 2, 9,  4]] # TRIAD_DIM


tick = 0
found = False
song_notes=[]
def get_notes_amount(track):
    beats = 0
    for msg in track:
        if type(msg) is Message:
            beats +=msg.time
    length= (beats+CHORD_DURATION-1)//CHORD_DURATION
    return length


#Get a proper chord for every note
def compute_beats(track):
    length=get_notes_amount(track)
    notes_list=[None]*length
    print(length)
    beats = 0
    last_note=0
    for msg in track:
       if type(msg) is Message:
            print(beats, beats//CHORD_DURATION,length)
            if(beats % CHORD_DURATION == 0 and msg.type =="note_on" ):
               song_notes.append(msg.note)
               if(notes_list[beats//CHORD_DURATION] is None):
                   notes_list[beats//CHORD_DURATION] = msg.note
               
            if(msg.type=="note_off"):
                last_note= msg.note
            beats +=msg.time
    if(beats % CHORD_DURATION == 0):
        notes_list[-1]=last_note
    print(notes_list)
    print(len(notes_list))
    return notes_list



tempo=0
for track in mid.tracks:
    for msg in track:
        if isinstance(msg, MetaMessage) and msg.type=="set_tempo":
            tempo=msg.tempo
tracks=[MetaMessage('set_tempo',tempo=tempo,time=0)]

song_notes=compute_beats(mid.tracks[1])
start_time=0
velocity= int(get_average_velocity()*0.9)
average_displacement= 12*(get_average_octave()-1)

final_genom_chord = Accompanement(MUSIC_SCALE, len(song_notes))
max_note=120

class Chromosome: 
    def __init__(self, size, genes_pool):
        self.size = size
        self.genes_pool = genes_pool
        self.rating= 0
        self.generate_random_genes()

    def generate_random_genes(self):
        for i in range(self.size):
            rand_note  = random.randint(0,max_note)
            rand_chord = Chord(rand_note,random.choice(ALL_CHORDS))
            self.genes_pool[i] = rand_chord

    def __eq__(self, other):
        return self.rating == other.rating 

    def __lt__(self, other):
        return self.rating < other.rating

def create_population(population_size, chromosome_size):
    population = [None]*population_size
    for i in range(population_size):
        population[i]= Chromosome(chromosome_size,[None]*chromosome_size);
    return population

def calculate_rating(population):
    for chromosome in population:
        chromosome.rating= chromosome.size
        for i in range(chromosome.size):
            if final_genom_chord.has_in_consonant_chords(chromosome.genes_pool[i]):
                chromosome.rating-=0.5
                if(song_notes[i] is None):
                    chromosome.rating-=0.5
                    continue
            if(song_notes[i] is not None and final_genom_chord.has_note_in_consonant_chords(song_notes[i]) and not chromosome.genes_pool[i].has_note(song_notes[i])):
                #chromosome.rating+=0.5
                chromosome.rating-=0
                
            else:
                chromosome.rating-=0.5
def print_population(population):
    i=0
    print(f"1. rating: {population[0].rating}  {len(population[0].genes_pool)}")
population_size=64
population= create_population(population_size, final_genom_chord.size)
calculate_rating(population)
population= sorted(population)
print_population(population)

survivors = [None] * (population_size // 4)

def select(population,survivors):
    size= len(survivors)
    for i in range(size):
        survivors[i]=population[i]

def get_parent_index(parents, other_parent_index):
    size= len(parents)
    while True:
        index = random.randint(0, size-1)
        if other_parent_index is None or other_parent_index!=index:
            return index
def cross(chromosome1, chromosome2):
    size = chromosome1.size
    point= random.randint(0,size-1)
    child = Chromosome(size,[None]*size)
    for i in range(point):
        child.genes_pool[i]=chromosome1.genes_pool[i]
    for i in range(point,size):
        child.genes_pool[i]=chromosome2.genes_pool[i]
    return child

def repopulate(population, parents, children_count):
    population_size = len(population)
    while children_count<population_size:
        p1_pos = get_parent_index(parents,None)
        p2_pos = get_parent_index(parents,p1_pos)
        population[children_count]=cross(parents[p1_pos],parents[p2_pos])
        population[children_count+1]=cross(parents[p2_pos],parents[p1_pos])
        children_count+=2


def mutate(population, chromosome_count, gene_count):
    pop_size = len(population)
    for i in range(chromosome_count):
        chromosome_pos = random.randint(0, pop_size - 1)
        chromo = population[chromosome_pos]
        for j in range(gene_count):
            rand_note  = random.randint(0,max_note)
            rand_chord = Chord(rand_note,random.choice(ALL_CHORDS))
            gene_pos = random.randint(0, chromo.size - 1)
            chromo.genes_pool[gene_pos] = rand_chord

iteration_count=0
max_iteration_count=10000
while True:
    iteration_count += 1
    calculate_rating(population)
    population = sorted(population)
    print(f"*** {str(iteration_count)}+ ***")
    print_population(population)
    if(population[0].rating==0 or iteration_count>max_iteration_count):
        break
    select(population,survivors)
    size=len(population)
    repopulate(population,survivors, population_size//2)
    mutate(population,size//2,1)

for chord in population[0].genes_pool:
      tracks.append(Message('note_on',channel=0,note=chord.note_list[0]+average_displacement,velocity=velocity,time=0))
      tracks.append(Message('note_on',channel=0,note=chord.note_list[1]+average_displacement,velocity=velocity,time=0))
      tracks.append(Message('note_on',channel=0,note=chord.note_list[2]+average_displacement,velocity=velocity,time=0))
      tracks.append(Message('note_off',channel=0,note=chord.note_list[0]+average_displacement,velocity=velocity,time=CHORD_DURATION))
      tracks.append(Message('note_off',channel=0,note=chord.note_list[1]+average_displacement,velocity=velocity,time=0))
      tracks.append(Message('note_off',channel=0,note=chord.note_list[2]+average_displacement,velocity=velocity,time=0))
mid.tracks.append(tracks)
mid.save("new_gen.mid")