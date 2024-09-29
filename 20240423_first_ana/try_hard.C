#include "/home/henrique/Dropbox/APC_Paris/Root/cold_box_analysis/class/MYCODES.h"

vector<Double_t> fit_sphe_wave0(Int_t ch = 0, Int_t rebin = 1, Double_t deconv = 4, Bool_t quite=true){
    
    Calibration Cal;
    
    
    Cal.rebin = rebin;
    Cal.channel = ch;
    Cal.quitemode = quite;
    string histogram = "analyzed_" + to_string(ch);
    Cal.rootFile = "sphe_histograms_Ch"+to_string(ch)+".root";

    Cal.dtime = 2; // steps (ADC's MS/s, 500 MS/s = 2 ns steps)

    Cal.make_free_stddevs = true; // starts with false, if good fitting, change to true
    Cal.searchParameters(histogram.c_str(), deconv, true); // give a first search in the parameters.

    Cal.deltaplus = 1;
    Cal.deltaminus = 0;

    // Cal.drawDebugLines = true;
    Cal.fit_sphe_wave(histogram.c_str(),false); // set true to make if you want to execute "searchParameters" inside here instead
    vector<Double_t> ret = {static_cast<Double_t>(Cal.fit_status), Cal.snr, Cal.chi2, Cal.ndf};
    return ret;
}

void try_hard(Int_t ch = 0, Double_t maxrebin = 2, Double_t max_sigma=8){
    gROOT->SetBatch(kTRUE);
    vector<Double_t> vals = {0,0,0,0};
    vector<Double_t> values_best_fit = {0,0,0,0};
    vector<Double_t> values_best_snr = {0,0,0,0};
    vector<Double_t> ref = {0,0,0,0};
    Double_t best_fit = 1e12;
    Double_t best_snr = 0;
    for (Int_t i = 2; i <= maxrebin; i*=2){
        for(Int_t j = 1; j <= max_sigma; j++){
            vals = fit_sphe_wave0(ch,i, j);
            if (vals[0] > 0){
                Double_t goodf = vals[2]/vals[3];
                if (goodf < best_fit){
                    best_fit = goodf;
                    values_best_fit = {static_cast<Double_t>(i), static_cast<Double_t>(j),vals[1],goodf};
                }
                if (vals[1] > best_snr){
                    best_snr = vals[1];
                    values_best_snr = {static_cast<Double_t>(i), static_cast<Double_t>(j),vals[1],goodf};
                }
            }
        }

    }
    gROOT->SetBatch(kFALSE);
    cout << "values_best_snr: " << values_best_snr[0] << " ";
    cout << values_best_snr[1] << " ";
    cout << values_best_snr[2] << " ";
    cout << values_best_snr[3] << endl;
    cout << "values_best_fit: " << values_best_fit[0] << " ";
    cout << values_best_fit[1] << " ";
    cout << values_best_fit[2] << " ";
    cout << values_best_fit[3] << endl;
    if (values_best_snr != values_best_fit){
        string Userchoise;
        cout << "Not cool!!" << endl;
        cout << "You have to pick one: SNR [s], Fit[f] ";
        cin >> Userchoise;
        if (Userchoise == "s")
        {
            cout << "Using best for SNR" << endl;
            values_best_fit = values_best_snr;
        }
        else if(Userchoise == "f")
        {
            cout << "Using best for Fit" << endl;
        }
        else{
            return;
        }
    }

    if(values_best_snr == ref){
        cout << "No fit works :( " << endl;
        return;
    }
    fit_sphe_wave0(ch, values_best_fit[0], values_best_fit[1], false);


}
