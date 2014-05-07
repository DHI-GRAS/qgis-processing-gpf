import java.io.IOException;
import org.esa.beam.framework.dataio.ProductIO;
import org.esa.beam.framework.datamodel.Product;
import org.esa.beam.framework.datamodel.MetadataElement;
import org.esa.beam.framework.datamodel.MetadataAttribute;
import org.esa.nest.datamodel.AbstractMetadata;


// Display all the bands names of the input image using BEAM to extract them.
// main takes two argument - the filename of the image and delimiter to prepend
// to band names to distinguish it from other output
class getNESTPixelSizes {
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