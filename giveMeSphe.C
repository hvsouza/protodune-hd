// ________________________________________ //
// Author: Henrique Souza
// Filename: giveMeSphe_darkCount.C
// Created: 2021
// ________________________________________ //
#include "/home/henrique/Dropbox/APC_Paris/Root/cold_box_analysis/class/MYCODES.h"


void adjust_parameters(SPHE2 &dark, int channel){
    switch (channel){
        case 0:
            dark.start = 3240;
            dark.finish = 4240;
            break;
        case 1:
            dark.start = 3240;
            dark.finish = 4240;
            break;
        case 2:
            dark.start = 3260;
            dark.finish = 4260;
            break;
        case 3:
            dark.start = 3260;
            dark.finish = 4260;
            break;
        case 4:
            dark.start = 3300;
            dark.finish = 4300;
            break;
        case 5:
            dark.start = 3300;
            dark.finish = 4300;
            break;
        case 6:
            dark.start = 3300;
            dark.finish = 4300;
            break;
        case 7:
            dark.start = 3300;
            dark.finish = 4300;
            break;
        case 34:
            dark.start = 2048;
            dark.finish = 2592;
            break;

    }

}

void giveMeSphe(int channel = 0){

    SPHE2 dark("spe");

    dark.led_calibration = true; // if external trigger + led was used, set true
                                 // start and finish will be the time of integration
    dark.just_a_test     = false; // well.. it is just a test, so `just_this` is the total waveforms analysed
    dark.just_this       = 200;
    dark.channel         = channel;
    dark.rootfile        = "analyzed.root";

    dark.start  = 2048;            // start the search for peaks or start the integration (led)
    dark.finish = 2640;        // fisish the search or finish the integration (led)

    dark.filter = 2;   // one dimentional denoise filter (0 equal no filder)



    dark.get_wave_form = true; // for getting spe waveforms
    dark.mean_before   = 0;   // time recorded before and after the peak found
    dark.mean_after    = 1024*16;

    dark.spe_max_val_at_time_cut = 1e12; // after `time_cut`, the signal cannot be higher than this
                                       // this allows to remove after pulses
    dark.time_cut = 2600; // in ns seconds
    dark.cut_with_filtered = true;

    dark.deltaplus  = 1.;
    dark.deltaminus = 0;


    dark.check_selection = true; // uses(or not) variable `selection` to discard wvfs
    dark.withfilter      = true; // Integrate in the filtered waveform
    dark.hnbins = 4000;
    dark.hxmin = -2.5;
    dark.hxmax = 40;
    dark.normalize_histogram = true;

    adjust_parameters(dark, channel);
    dark.giveMeSphe();



    gROOT->SetBatch(kFALSE);

   
}
