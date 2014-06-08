#!/usr/bin/groovy

// TODO: use streams to create cat() method (just to see how it works)

/*
 * Simple cat implementation in Groovy.
 */
class Cat {

    /*
     * Method implementing main function.
     */
    static void main(String[] args) {
        int retcode = 0
        if (args.size() == 0) {
            // this will catch keyborad exception and return 130 by default
            new InputStreamReader(System.in).eachLine { line -> println(line) }
            System.exit(retcode)
        }
        args.each { filename ->
            try {
                new File(filename).eachLine { line -> println(line) } 
            } catch (java.io.IOException ex) {
                System.err.println(ex)
                retcode = 1
            }
        }
        System.exit(retcode)
    }
}
