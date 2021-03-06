package pid.kaon

import org.jlab.clas.pdg.PDGDatabase
import org.jlab.detector.base.DetectorType
import event.Event


class KaonMinusPID{

    def ebPID = 0
    def charge = 0

    def kaonMinusPDG = -321

    //dcr1,2,3 fiducial cut parameters    
    def sect_angle_coverage = 60
    // height is lower for outbending runs - this parameter is field config. / sector dependent
    def heightR1 = 16
    def radiusR1 = 25

    def heightR2 = 30
    def radiusR2 = 41

    def heightR3 = 52
    def radiusR3 = 71

    //these need to be stored elsewhere- need to plan out a cut DB procedure
    def km_beta_mean_p0 = [1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
    def km_beta_mean_p1 = [0.244, 0.244, 0.244, 0.244, 0.244, 0.244]
    def km_beta_sig_p0 = [0.0048138, 0.00520169, 0.00570919, 0.0062253, 0.00617771, 0.00578081]
    def km_beta_sig_p1 = [-0.000382083, -0.000771668, -0.00179812, -0.00299382, -0.00282061, -0.00191396]
    def km_beta_sig_p2 = [0.00617906, 0.00592537, 0.00671878, 0.00752452, 0.00707839, 0.00691364]

    def km_beta_sig_range = 3.0


    def passKaonMinusEBPIDCut = { event, index ->
	return (event.pid[index] == kaonMinusPDG)
    }


    // FIDUCIAL CUTS ON DC
    //detector layer r1-12, r2-24, r3-36
    //rotate hit position based on sector
    def rotateDCHitPosition(hit, sec) {
        def ang = Math.toRadians(sec * sect_angle_coverage)
        def x1_rot = hit.get(1) * Math.sin(ang) + hit.get(0) * Math.cos(ang)
        def y1_rot = hit.get(1) * Math.cos(ang) - hit.get(0) * Math.sin(ang)
        return [x1_rot, y1_rot]
    }

    //define left right 
    def borderDCHitPosition(y_rot, height) {
        def slope = 1 / Math.tan(Math.toRadians(0.5 * sect_angle_coverage))
        def left = (height - slope * y_rot)
        def right = (height + slope * y_rot)
        return [left, right]
    }

    def passKaonMinusDCR1 = {event, index ->
	if (event.dc1_status.contains(index)){
	    def sec = event.dc_sector[index]
	    def hit = event.dc1.get(index).find{ hit -> hit.layer == 12}
            if (hit){
                def hit_rotate = rotateDCHitPosition([hit.x, hit.y], sec-1)
                def left_right = borderDCHitPosition(hit_rotate.get(1), heightR1)
                return (hit_rotate.get(0) > left_right.get(0) && hit_rotate.get(0) > left_right.get(1))
            } else {
                return false
            }
	}
	return false
    }
    
    def passKaonMinusDCR2 = { event, index ->
	if (event.dc2_status.contains(index)){
	    def sec = event.dc_sector[index]
	    def hit = event.dc2.get(index).find{ hit -> hit.layer == 24}
            if (hit){
                def hit_rotate = rotateDCHitPosition([hit.x, hit.y], sec-1)
                def left_right = borderDCHitPosition(hit_rotate.get(1), heightR2)
                return (hit_rotate.get(0) > left_right.get(0) && hit_rotate.get(0) > left_right.get(1))
            } else {
                return false
            }
	}
	return false
    }

    def passKaonMinusDCR3 = { event, index ->
	if (event.dc3_status.contains(index)){
	    def sec = event.dc_sector[index]
	    def hit = event.dc3.get(index).find{ hit -> hit.layer == 36}
	    if (hit) {
                def hit_rotate = rotateDCHitPosition([hit.x, hit.y], sec-1)
                def left_right = borderDCHitPosition(hit_rotate.get(1), heightR3)

                // from lower line: && x1_rot**2 > radius2_DCr1){ return true }
                return (hit_rotate.get(0) > left_right.get(0) && hit_rotate.get(0) > left_right.get(1))
            } else {
                return false
            }
	}
	return false
    }


    def passKaonMinusBetaFitCut = {event, index ->

	if( event.tof_status.contains(index) ){
	    def ftof_sector = event.tof_sector[index]
	    def particle_beta =  event.beta[index]
	    def p = event.p[index]
	    def mean = km_beta_mean_p0[sect] * p / Math.sqrt(p**2 + km_beta_mean_p1[sect]) 
	    def sigma = km_beta_sig_p0[sect] + km_beta_sig_p1[sect]/Math.sqrt(p) + km_beta_sig_p2[sect]/(p**2)
	    // CHANGE 
	    def beta_upper = mean + km_beta_sig_range*sigma
	    def beta_lower = mean - km_beta_sig_range*sigma

	    if( particle_beta <= beta_upper && particle_beta >= beta_lower ){
		return true
	    }	    	    
	}
	return false

	//add central beta cut in here to
    }

    


}
