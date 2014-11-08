""" Experiment:
Setup for tDCS bodyspec, including release RT's
"""
# TO DO
    # check whether we want to add a sleep to "Ready?" just so it's always there
    # see whether theres a way to do faster tracking of early release during Ready and fixation
    # add s/t to track trials restarted b/o early release
    # where to add feedback? e.g. double key release during stim? 
    # check whether we want to pseudorandomize!
    # add practice trials
    # add instructions
##########
# Import #
##########
import pygame
import pygame.locals as loc
import random, numpy
import os, csv, sys, time

##################
# Classes & Defs #
##################
class Trial:
    n_trial = 0 # tracks trial number 

    def __init__(self, stiminfo): 
        """ Set up the relevant variables for a given trial
        """
        Trial.n_trial += 1 # increment trial number
        self.trial_rep_n = 0 # tracks whether a given trial is restarted before stim 
        self.background = SCREEN

        # set trial specific values
        self.word = stiminfo[0]
        self.stim_type = stiminfo[1]
        self.n = self.n_trial
        self.fix_dur = random.uniform(.75, 1.25)
        if LAB_VERSION == 'O':
            self.labels = (stiminfo[2], stiminfo[3])
        elif LAB_VERSION == 'F':
            self.labels = (stiminfo[3], stiminfo[2])

        # sets the text object for ready & warning cues
        self.cue = MultiText(SCREEN,CENTER)
        # sets the text object for stim & resp labels
        self.stim = MultiText(SCREEN, CENTER, resp_labels = True)
        # set home and response key variables
        self.home_keys = [loc.K_d, loc.K_k]
        self.resp_keys = [loc.K_e, loc.K_i]
        

    def run(self):
        """ Set up the different stages of stim presentation and resp logging
        for a given trial"""
        self.trial_rep_n += 1 # increment trial presentation counter
        # Show Ready cue
        self.cue.show('Ready?')
        pygame.display.update()
        self.trial_onset = time.time() # log Ready cue onset time
        # Wait for Ss to press the two home keys
        while 1:
            if monitor_key_down(self.home_keys):
                self.home_key_press_time = time.time() # log home key presstime
                break
            else:
                continue
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
        self.stim.show('to ' + self.word, self.labels)
        pygame.display.update()
        self.stim_onset = time.time()

        # Start monitoring for responses
        # set up lists for logging responses, monitoring for multiple resps
        self.release_resp = []
        self.release_time =[]
        self.press_resp = []
        self.press_time = []
        pygame.event.clear() # clear the event queue to make sure we're starting fresh
        events = None 
        # start monitoring
        while 1:
            events = pygame.event.get() # gets the last event and removes from queue
            if not events: # if no keys have been released or pressed yet
                continue # keep polling for key events
            event = events[0] # pull out the relevant event
            # if this is a key release
            if event.type == loc.KEYUP:
                self.release_time.append(str("{:.6f}".format(time.time()))) # log the time
                self.release_resp.append(chr(event.key)) # log the response
            # if this is a key_press
            elif event.type == loc.KEYDOWN:
                    self.press_time.append(str("{:.6f}".format(time.time()))) # log the time
                    self.press_resp.append(chr(event.key)) # log the response
                # if the key is a response key
                    if event.key in self.resp_keys: 
                        break
                    elif event.key in self.home_keys:
                        continue

        # Clear screen and wait for ITI
        self.background.fill((0, 0, 0))
        pygame.display.flip()
        time.sleep(1)

    def write_data(self, save_file):
        trial_info = [str(SUB_NUM), self.word, str(self.n), str(self.fix_dur),
                      ';'.join(self.release_resp),
                      ';'.join(self.press_resp),
                      "{:.6f}".format(self.trial_onset),
                      "{:.6f}".format(self.home_key_press_time),
                      "{:.6f}".format(self.stim_onset), 
                      ';'.join(self.release_time),
                      ';'.join(self.press_time),
                      str(self.trial_rep_n)]
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
        self.label_pos_L = [(self.pos[0]/4)*3, (self.pos[1]/5)*7]
        self.label_pos_R = [(self.pos[0]/4)*5, (self.pos[1]/5)*7]
        
    def show(self, text, labels = None, color = [255,255,255]):        
        # set the stimulus text
        self.rend_text = self.font.render(text, True, color)
        self.text_rect = self.rend_text.get_rect()
        self.text_rect.centerx = self.pos[0]
        self.text_rect.centery = self.pos[1]
        self.screen.blit(self.rend_text, self.text_rect)
        
        # add response labels
        if self.resp_labels:
        	self.rend_label_L = self.font.render(labels[0], True, color)
	        self.rend_label_R = self.font.render(labels[1], True, color)
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
    header = 'subject, stim, trial_n, fix_dur, release_resp,\
    press_resp, trial_onset, home_key_press_time, stim_onset,\
    release_time, press_time,trial_rep_counter'

    save_file.writelines(header + '\n')

    # get the stims in
    stimfile = 'Bomb_tDCS_stims.csv'
    reader = csv.reader(open(stimfile,'rU'), dialect = 'excel')
    headerline = reader.next()
    verb_list = [row for row in reader]
    random.shuffle(verb_list)    

    trials = [Trial(stim_info) for stim_info in verb_list]

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
    for t in trials[:10]:
        t.run()
        t.write_data(save_file)

    # And we're done
    instruct.show("* That's it! Thanks for participating! *")
    pygame.display.update()
    wait_for_response(loc.K_ESCAPE)

#################
### Run study ###
#################
if __name__ == '__main__':
    main()
