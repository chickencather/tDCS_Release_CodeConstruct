""" Experiment:
Setup for tDCS bodyspec, including release RT's
"""
# TO DO
# check whether we want to add a sleep to "Ready?" just so it's always there
# check how to do feedback/monitoring for early release
# add s/t to track trials restarted b/o early release
# see whether the key release tracker has enough resolution to measure 
# near simultaneous key releases. if not, have it grab *everything* that is a keyup
import pygame
import pygame.locals as loc
import random
import sys
import os
import time
import numpy

class Trial:
    n_trial = 0

    def __init__(self, word, left_label): 
        """ Set up the relevant variables for a given trial
        """
        Trial.n_trial += 1
        self.word = word
        #self.resp = ''
        self.n = self.n_trial
        
        self.background = SCREEN
        # sets the text object for ready & warning cues
        self.cue = MultiText(SCREEN,CENTER)
        # sets the text object for stinm & resp labels
        self.stim = MultiText(SCREEN, CENTER, resp_labels = True)
        self.fix_dur = random.uniform(.75, 1.25)

        # set response key variable
        self.home_keys = [loc.K_d, loc.K_k]
        self.resp_keys = [loc.K_e, loc.K_i]

    def run(self):
        """ Set up the different stages of stim presentation and resp logging
        for a given trial"""
        # runs the separate stimuli 
        # Show Ready cue
        self.cue.show('Ready?')
        pygame.display.update()
        self.trial_onset = time.time()
        # Wait for Ss to press the two home keys
        #self.init = wait_for_init(self.home_keys)
        while 1:
            if monitor_key_down(self.home_keys):
                break
            else:
                continue

            

        self.home_button_press = time.time()
        # make sure ready stays on the screen for at least 300 ms
        time.sleep(.3)
        
        # Show fixation
        self.background.fill((0, 0, 0))
        pygame.display.flip()
        center = [d/2 for d in self.background.get_size()] 
        pygame.draw.circle(self.background, (255, 255, 255), center, 10)
        pygame.display.flip()
        time.sleep(self.fix_dur)
        self.background.fill((0, 0, 0))
        pygame.display.flip()

        # flash warning and restart trial if Ss release home keys too early
        if not monitor_key_down(self.home_keys):
            # flash warning
            self.cue.show('TOO SOON!', color = [255,0,0])
            pygame.display.flip()
            time.sleep(1)
            self.background.fill((0, 0, 0))
            pygame.display.flip()
            # restart the trial
            self.run() 
            # ADD TRIAL LOGGER HERE
            return None

        # Show stimulus
        self.stim.show(self.word)
        pygame.display.update()
        self.stim_onset = time.time()

        # New response logging
        self.release_resp = []
        self.release_time =[]
        pygame.event.clear()
        events = None
        while 1:
            events = pygame.event.get()
            if not events:
                continue
            # ignores more than one event; NOTE might wanna change this
            event = events[0]
            # if this is a key release
            if event.type == loc.KEYUP:
                # log the time
                self.release_time.append(time.time())
                self.release_resp.append(chr(event.key)) #
                print 'release'
                print self.release_resp
                print self.release_time

            # if this is a key_press
            elif event.type == loc.KEYDOWN:
                if event.key in self.resp_keys:
                    # log_stuff
                    print 'press'
                    self.press = 'press_placeholder'
                    break
                # elif self.releases[-1] == whatever and event.key == blah:
                #     print 'incompatible loop'
                    #do_stuff()


        # Clear screen and wait for ITI
        self.background.fill((0, 0, 0))
        pygame.display.flip()
        time.sleep(1)



        # Get the response
        # # make sure that one finger always stays on d or k
        # self.release = wait_for_response(self.home_keys, resp_type=loc.KEYUP)
        # self.release_time = time.time()
        # self.press = wait_for_response(self.resp_keys)
        # self.travel_time = time.time()

        # # # Or...
        # self.releases = []
        # pygame.event.clear()
        # while 1:
        #     events = pygame.event.get()
        #     event = events[0] # ignores more than one event
        #     if event.type == RELEASE:
        #         self.release_time.append(time.time())
        #         self.releases.append(chr(event.key)) #name
        #     elif event.type == PRESS:
        #         if event.key in response_keys:
        #             log_stuff
        #             break
        #         elif self.releases[-1] == whatever and event.key == blah:
        #             do_stuff()




        # # Clear screen and wait for ITI
        # self.background.fill((0, 0, 0))
        # pygame.display.flip()
        # time.sleep(1)

    def write_data(self, save_file):
        trial_info = [str(SUB_NUM), self.word, str(self.release_resp)] #, self.press,
        #               str(self.n), 
        #               "{:.6f}".format(self.trial_onset),
        #               "{:.6f}".format(self.home_button_press),
        #               str(self.fix_dur),
        #               "{:.6f}".format(self.stim_onset), 
        #               "{:.6f}".format(self.release_time),
        #               "{:.6f}".format(self.travel_time),
        #               #str(self.release_time - self.stim_onset),
        #               str(self.travel_time - self.release_time)]
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
        
    def show(self, text, color = [255,255,255]):
         
        #self.color = color

        # set the stimulus text
        self.rend_text = self.font.render(text, True, color)
        self.text_rect = self.rend_text.get_rect()
        self.text_rect.centerx = self.pos[0]
        self.text_rect.centery = self.pos[1]
        self.screen.blit(self.rend_text, self.text_rect)
        
        # add response labels
        if self.resp_labels:
        	self.rend_label_L = self.font.render(self.label[0], True, color)
	        self.rend_label_R = self.font.render(self.label[1], True, color)
	        self.screen.blit(self.rend_label_L, self.label_pos_L)
	        self.screen.blit(self.rend_label_R, self.label_pos_R)
	        
def monitor_key_down(keylist):
    """ Checks whether keys are still held down"""
    keys_expected = numpy.zeros(len(pygame.key.get_pressed()))
    keys_expected[keylist] = 1
    pygame.event.clear()
    keys_pressed = list(pygame.key.get_pressed())
    # if all required keys are pressed
    if numpy.all(keys_expected == keys_pressed):
        return True

def wait_for_init(keylist, limit = 1000):
    """ Waits for key(s) to be held to initialize trial
    """
    #time_start = time.time()
    # define which keys are to be pressed
    keys_expected = numpy.zeros(len(pygame.key.get_pressed()))
    keys_expected[keylist] = 1
    pygame.event.clear()
    # start monitoring keypresses
    while True:
        pygame.event.clear()
        keys_pressed = list(pygame.key.get_pressed())
        # if all required keys are pressed
        if numpy.all(keys_expected == keys_pressed):
            return False
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
            print chr(event[0].key)
            #print event[1]
            print event
            return chr(event[0].key)

def main():
    global TDCS_VERSION, LAB_VERSION, SCREEN, CENTER, SUB_NUM
    if len(sys.argv) > 1:
        SUB_NUM = sys.argv[1]
    else:
        SUB_NUM = raw_input('Subject number: ')

    TDCS_VERSION = None
    LAB_VERSION = None    
    while TDCS_VERSION not in ('L', 'R'):
        TDCS_VERSION = raw_input('Red Pos: ')
    while LAB_VERSION not in ('O', 'F'):
        LAB_VERSION = raw_input('Lab_Ver: ')
    pygame.init()
    pygame.mouse.set_visible(False)
    SCREEN = pygame.display.set_mode((0,0), loc.FULLSCREEN) 
    CENTER = [SCREEN.get_size()[0]/2, (SCREEN.get_size()[1] / 2)]
    
    # intializes a simpletext instance; can hold different (?) strings
    instruct = MultiText(SCREEN, CENTER)

    # Initialize data file
    fname = 'data/' + SUB_NUM + '.csv'
    if os.path.exists(fname):
       raise(Exception('File %s already exists.' % fname))
    else:
        save_file = open(fname, 'wb')
    # set up the header for the output file
    header = 'subject,stim,release_resp,press_resp,trial_n,trial_onset,\
    home_button_press,fix_dur,stim_onset,rel_time,trav_time,\
    rel_rt,trav_rt'
    save_file.writelines(header + '\n')

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
    stim_info = [['run', 'yes'], ['kick', 'no']]

    trials = [Trial(*s) for s in stim_info]

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
        t.write_data(save_file)

    # And we're done
    instruct.show("* That's it! Thanks for participating! *")
    pygame.display.update()
    wait_for_response(loc.K_ESCAPE)


### Run study
if __name__ == '__main__':
    main()
