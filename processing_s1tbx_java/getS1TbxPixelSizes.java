/*
***************************************************************************
    getS1TbxPixelSize.java
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
import org.esa.beam.framework.datamodel.Product;
import org.esa.beam.framework.datamodel.MetadataElement;
import org.esa.beam.framework.datamodel.MetadataAttribute;
import org.esa.snap.datamodel.AbstractMetadata;


// Display all the bands names of the input image using BEAM to extract them.
// main takes two argument - the filename of the image and delimiter to prepend
// to band names to distinguish it from other output
class getS1TbxPixelSizes {
    private static Product product;
 
    public static void main(String[] args) {

        if (args.length >= 1) {
        	try{	
        		product = ProductIO.readProduct(args[0]);
        		String delim;
        		if (args.length >= 2)
        			delim = args[1];
        		else
        			delim = "";
        		
        		MetadataElement metadata = AbstractMetadata.getAbstractedMetadata(product);
        		MetadataAttribute range_spacing = metadata.getAttribute("range_spacing");
        		MetadataAttribute azimuth_spacing = metadata.getAttribute("azimuth_spacing");	
                if (range_spacing != null && azimuth_spacing != null){
                	System.out.println("Range spacing"+delim+range_spacing.getData()+delim+range_spacing.getUnit());
                	System.out.println("Azimuth spacing"+delim+azimuth_spacing.getData()+delim+azimuth_spacing.getUnit());
                }
                product.closeIO();
        	} catch (IOException e) {
        		// if the file can't be found just do nothing
        	}
        }
    }
}