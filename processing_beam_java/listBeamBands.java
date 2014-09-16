/*
***************************************************************************
    listBeamBands.java
-------------------------------------
    Copyright (C) 2014 TIGER-NET (www.tiger-net.org)

***************************************************************************
* This plugin is part of the Water Observation Information System (WOIS)  *
* developed under the TIGER-NET project funded by the European Space      *
* Agency as part of the long-term TIGER initiative aiming at promoting    *
* the use of Earth Observation (EO) for improved Integrated Water         *
* Resources Management (IWRM) in Africa.                                  *
*                                                                         *
* WOIS is a free software i.e. you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published       *
* by the Free Software Foundation, either version 3 of the License,       *
* or (at your option) any later version.                                  *
*                                                                         *
* WOIS is distributed in the hope that it will be useful, but WITHOUT ANY * 
* WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License   *
* for more details.                                                       *
*                                                                         *
* You should have received a copy of the GNU General Public License along *
* with this program.  If not, see <http://www.gnu.org/licenses/>.         *
***************************************************************************
*/

import java.io.IOException;
import org.esa.beam.framework.dataio.ProductIO;
import org.esa.beam.framework.datamodel.Band;
import org.esa.beam.framework.datamodel.Product;

// Display all the bands names of the input image using BEAM to extract them.
// main takes two argument - the filename of the image and delimiter to prepend
// to band names to distinguish it from other output
class listBeamBands {
    private static Product product;
 
    public static void main(String[] args) {

        if (args.length >= 1) {
        	try{	
        		product = ProductIO.readProduct(args[0]);
        		String bandDelim;
        		String appendProductName = "";
        		if (args.length >= 2)
        			bandDelim = args[1];
        		else
        			bandDelim = "";
        		if (args.length >= 3)
        			appendProductName = args[2];
        		Band[] bands = product.getBands();
                for (Band band : bands) {
                	if (appendProductName.equals("True"))
                		System.out.println(bandDelim+band.getName()+"::"+product.getName());
                	else
                		System.out.println(bandDelim+band.getName());
                }
                product.closeIO();
        	} catch (IOException e) {
        		// if the file can't be found just do nothing
        	}
        }
    }
}