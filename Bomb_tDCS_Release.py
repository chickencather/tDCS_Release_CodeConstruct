""" Experiment:
Play a series of beeps from a soundfile.
Show a phrase.
Collect binary sensicality judgments for that phrase.
    Press Y if sensible, N if not sensible.
This is like a lexical decision task, but for phrases.
So participants would rate "green tomato soup" as sensical,
    and "purple monkey dishwasher" as nonsensical.

Randomize which specific chirp stims go in each category.
    Categories: Structure (right/left) X Pitch (same/diff)

Things to check in output:
    EXP_VERSION correctly balances which targets get which structure?
    Faster beeps? I have no idea if this is going to work.

EXP_VERSION (0,1) controls which targets get a left- vs right-structure.
"""

import pygame
import pygame.locals as loc
import random
import sys
import os
import time
import numpy

class Trial:
    n_trial = 0

    def __init__(self, word): 
        Trial.n_trial += 1
        self.word = word
        self.resp = ''
        self.n = self.n_trial
        
        self.background = SCREEN
        self.ready = MultiText(SCREEN,CENTER)
        self.text = MultiText(SCREEN, CENTER, resp_labels = True)
        self.fix_dur = random.uniform(.75, 1.25)

    def run(self):
        # Show Ready cue
        self.ready.show('Ready?')
        pygame.display.update()
        self.init = wait_for_init([loc.K_d, loc.K_k])
		# make sure ready stays on the screen for at least 300 ms
        time.sleep(.3)

        # Show fixation
        self.background.fill((0, 0, 0))
        pygame.display.flip()
        center = [d/2 for d in self.background.get_size()] 
        pygame.draw.circle(self.background, (255, 255, 255), center, 10)
        pygame.display.flip()
        # make sure they're not releasing the buttons here
        while wait_for_init([loc.K_d, loc.K_k]):
        	time.sleep(self.fix_dur)


        # Show stimulus
        self.background.fill((0, 0, 0))
        pygame.display.flip()
        self.text.show(self.word)
        pygame.display.update()
        self.stim_onset = time.time()

        # Get the response
        # make sure that one finger always stays on d or k
        self.resp = wait_for_response((loc.K_e, loc.K_i))
        self.resp_time = time.time()

        # Clear screen and wait for ITI
        self.background.fill((0, 0, 0))
        pygame.display.flip()
        time.sleep(1)

    def write_data(self, save_file):
        trial_info = [str(SUB_NUM), self.word, self.resp,
                      str(self.n), str(self.fix_dur),
                      "{:.6f}".format(self.start_time), 
                      "{:.6f}".format(self.resp_time),
                      str(self.resp_time - self.start_time)]
        line = ','.join(trial_info) + '\n'
        save_file.writelines([line])
        save_file.flush()

class MultiText:
    def __init__(self, screen, pos, resp_labels = False, font_size=52):
        """ Writes a single text stim to the screen.
        If resp_labels is set to true, response labels are added as well.
        """
        self.screen = screen
        self.font = pygame.font.Font(None, font_size)
        self.resp_labels = resp_labels
        # provide the x & y coordinates for blitting location
        self.pos = pos
        # set up the labels and their positions
        self.label = ('yes', 'no')
        self.label_pos_L = [(self.pos[0]/4)*3, (self.pos[1]/5)*7]
        self.label_pos_R = [(self.pos[0]/4)*5, (self.pos[1]/5)*7]
        
    def show(self, text):
        # set the stimulus text
        self.rend_text = self.font.render(text, True, [255,255,255])
        self.text_rect = self.rend_text.get_rect()
        self.text_rect.centerx = self.pos[0]
        self.text_rect.centery = self.pos[1]
        self.screen.blit(self.rend_text, self.text_rect)
        
        # add response labels
        if self.resp_labels:
        	self.rend_label_L = self.font.render(self.label[0], True, [255,255,255])
	        self.rend_label_R = self.font.render(self.label[1], True, [255,255,255])
	        self.screen.blit(self.rend_label_L, self.label_pos_L)
	        self.screen.blit(self.rend_label_R, self.label_pos_R)
	        

def wait_for_init(keylist, limit = 1000):
	""" Waits for key(s) to be held to initialize trial
	"""
	#time_start = time.time()
	# define which keys are to be pressed
	keys_expected = numpy.zeros(len(pygame.key.get_pressed()))
	keys_expected[keylist] = 1

	# start monitoring keypresses
	while True:
		pygame.event.clear()
		keys_pressed = list(pygame.key.get_pressed())
		# if all required keys are pressed
		if numpy.all(keys_expected == keys_pressed):
			break
			
def wait_for_response(keylist, limit=1000, resp_type=loc.KEYDOWN):
    """ Wait for a keypress, then go on.
    """
    time_start = time.time()
    if type(keylist) not in (list, tuple):
        keylist = [keylist]
    pygame.event.clear()
    while True:
        event = pygame.event.get(resp_type)
        if time.time() > time_start + limit:
            break
        elif not event:
            continue
        elif event[0].key in keylist:
            return chr(event[0].key)

def main():
    global EXP_VERSION, SCREEN, CENTER, SUB_NUM
    if len(sys.argv) > 1:
        SUB_NUM = sys.argv[1]
    else:
        SUB_NUM = raw_input('Subject number: ')
    #EXP_VERSION = int(SUB_NUM) % 2
    pygame.init()
    pygame.mouse.set_visible(False)
    SCREEN = pygame.display.set_mode((0,0), loc.FULLSCREEN) 
    CENTER = [SCREEN.get_size()[0]/2, (SCREEN.get_size()[1] / 2)]
    print CENTER
    # intializes a simpletext instance; can hold different (?) strings
    instruct = MultiText(SCREEN, CENTER)

    # Initialize data file
    # fname = 'data/' + SUB_NUM + '.csv'
    # if os.path.exists(fname):
    #    raise(Exception('File %s already exists.' % fname))
    # else:
    #    save_file = open(fname, 'wb')
    
    # header = 'subject,stim,response,trial, fix_dur, time_stim,time_resp, rt_resp'
    # save_file.writelines(header + '\n')

    # text stims
    # f = open('../stims/filler_phrases.txt')
    # filler = [line.strip() for line in f.readlines()]
    # initial_filler = filler[-2:]
    # filler_phrases = filler[:-2]
    # f = open('../stims/target_phrases.txt')
    # all_targets = [line.strip() for line in f.readlines()]
    # all_targets = zip(*[e.split(',') for e in all_targets])
    # all_right_targets = list(all_targets[0])
    # all_left_targets = list(all_targets[1])
    # n_targs = len(all_left_targets)

    # Make a list of all targets to be used in the experiment.
    # 2 lists: left-targets and right-targets
    #   Different items assigned to left- & right-branching for diff EXP_VERSION
    # EXP_VERSION balances which phrases are shown w/ right vs left structure.
    # if EXP_VERSION == 0:
    #     left_targets = all_left_targets[n_targs/2:]
    #     right_targets = all_right_targets[:n_targs/2]
    # elif EXP_VERSION == 1:
    #     left_targets = all_left_targets[:n_targs/2]
    #     right_targets = all_right_targets[n_targs/2:] 
    # random.shuffle(left_targets)
    # random.shuffle(right_targets)
    # #stim_targets = left_targets + right_targets
    # text_condition = (['left'] * (n_targs/2)) + (['right'] * (n_targs/2))

    # Assemble dictionary of chirps in the different conditions.
    # Randomize the order of chirps within conditions.
    # Assign 1/2 the chirps in each condition to target, 1/2 to filler.
    # chirp_names = {'left': {'same': [], 'diff': []},
    #                'right': {'same': [], 'diff': []}}
    # l_target_chirps = []
    # r_target_chirps = []
    # filler_chirps = []
    # for branch in ['left', 'right']:
    #     for pitch in ['same', 'diff']:
    #         for n in range(n_targs/2): # w/ 48 targets, this goes to 24
    #             chirp_name = 'branch_%s_%d_%s.wav' % (branch, n, pitch)
    #             # Add to chirp_names list
    #             chirp_names[branch][pitch].append(chirp_name)
    #         # Put a random selection of 12 chirps from each
    #         # branching-pitch category into lists to be bound
    #         # with target and filler phrases. To make sure that
    #         # the left- and right-branching phrases have the
    #         # same number of chirps from each category, assign
    #         # chirps separately to left- and right-branching phrases.
    #         random.shuffle(chirp_names[branch][pitch])
    #         chunk_size = n_targs / 4
    #         cond_chirps = chirp_names[branch][pitch] 
    #         l_target_chirps += cond_chirps[:chunk_size/2]
    #         r_target_chirps += cond_chirps[chunk_size/2:chunk_size]
    #         filler_chirps += cond_chirps[chunk_size:]

    # # Put together the stim information into trials.
    # target_phrases = left_targets + right_targets
    # target_conditions = (['left'] * (n_targs/2)) + (['right'] * (n_targs/2))
    # target_chirps = l_target_chirps + r_target_chirps
    # targ_info = zip(target_phrases, target_conditions, target_chirps)

    # fill_info = zip(filler_phrases, ['filler'] * n_targs, filler_chirps)
    # stim_info = targ_info + fill_info
    # random.shuffle(stim_info)

    # # Start with 2 filler trials
    # initial_stims = zip(initial_filler,
    #                     ['filler', 'filler'],
    #                     ['init_filler_l.wav', 'init_filler_r.wav'])
    stim_info = ['run', 'kick']

    trials = [Trial(s) for s in stim_info]

    ##############################
    ##### Run the experiment #####
    ##############################

    # Wait for a keypress to begin
    instruct.show("Press SPACE to begin.")
    pygame.display.update()
    wait_for_response(loc.K_SPACE)
    SCREEN.fill((0, 0, 0))
    pygame.display.flip()

    # Run the trials
    for t in trials:
        t.run()
        #t.write_data(save_file)

    # And we're done
    instruct.show("* That's it! Thanks for participating! *")
    pygame.display.update()
    wait_for_response(loc.K_ESCAPE)


### Run study
if __name__ == '__main__':
    main()
