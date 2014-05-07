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