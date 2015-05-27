#!/usr/bin/groovy

/*
 * Read and print content of a file object.
 */
static void cat(file) {
    file.eachLine { line -> println(line) }
}

/*
 * Method of main function.
 */
static void main(String[] args) {
    int retcode = 0
    if (args.size() == 0) {
        // this will catch keyborad exception and return 130 by default
        cat(new InputStreamReader(System.in))
        System.exit(retcode)
    }
    args.each { filename ->
        try {
            cat(new File(filename))
        } catch (java.io.IOException ex) {
            System.err.println(ex)
            retcode = 1
        }
    }
    System.exit(retcode)
}
